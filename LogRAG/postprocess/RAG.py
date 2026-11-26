import os
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain.prompts import PromptTemplate
from langchain_community.llms import HuggingFacePipeline
from langchain.chains import LLMChain
from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
import pandas as pd 
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from tqdm import tqdm 
import json
from openai import OpenAI
import numpy as np
from postprocess.prompts import prompt1, prompt2, prompt3, prompt4, prompt5
import importlib
import torch, gc

class RAGPostProcessor:
    def __init__(self, configs, train_data_path, logger):
        self.train_data_path = train_data_path
        self.llm_name = configs['llm_name']
        self.llm_backend = configs.get('llm_backend', 'openai')
        self.embedding_backend = configs.get('embedding_backend', 'openai')
        self.embedding_model = configs.get(
            'embedding_model', 'text-embedding-ada-002'
        )
        self.embedding_device = configs.get('embedding_device', 'cpu')
        self.threshold = configs['threshold']
        self.topk = configs['topk']
        self.api_key = configs['api_key']
        self.api_base = configs['api_base']
        self.ollama_base_url = configs.get(
            'ollama_base_url', 'http://127.0.0.1:11434'
        )
        self.ollama_num_ctx = configs.get('ollama_num_ctx', 4096)
        self.ollama_num_predict = configs.get('ollama_num_predict', 512)
        self.persist_directory = configs['persist_directory']
        self.output_dir = configs.get('output_dir', './output')
        self.device = configs['device']
        self.prompt = self._import_prompt(configs['prompt'])
        self.logger = logger
        self.model_activity = {
            "chat_backend": self.llm_backend,
            "chat_model": self.llm_name,
            "embedding_backend": self.embedding_backend,
            "embedding_model": self.embedding_model,
            "embedded_documents": 0,
            "chat_queries": 0,
            "json_repair_queries": 0,
        }

    def _import_prompt(self, prompt_name):
        # 动态导入 postprocess.prompts 模块
        module = importlib.import_module('postprocess.prompts')
        # 获取对应的 prompt 对象
        return getattr(module, prompt_name)

    @staticmethod
    def _parse_json_object(content):
        decoder = json.JSONDecoder()
        for start, character in enumerate(content):
            if character != "{":
                continue
            try:
                result, _ = decoder.raw_decode(content[start:])
            except json.JSONDecodeError:
                continue
            if isinstance(result, dict) and "is_anomaly" in result:
                return result
        raise ValueError(
            "No JSON object with is_anomaly found in chat model response"
        )

    def get_llm(self, llm_name):
        if self.llm_backend == "openai":
            return ChatOpenAI(
                model_name=llm_name,
                temperature=0,
                api_key=self.api_key,
                base_url=self.api_base,
            )
        if self.llm_backend == "ollama":
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            return ChatOllama(
                model=llm_name,
                base_url=self.ollama_base_url,
                temperature=0,
                num_ctx=self.ollama_num_ctx,
                num_predict=self.ollama_num_predict,
            )
        if self.llm_backend == "transformers":
            llm = self.get_local_llm(llm_name)
            return llm
        raise ValueError(f"Unsupported LogRAG chat backend: {self.llm_backend}")

    def ask_ChatGPT(self, prompt_content):
        self.model_activity["json_repair_queries"] += 1
        if self.llm_backend == "openai":
            client = OpenAI(
                base_url=self.api_base,
                api_key=self.api_key,
            )
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt_content
                    }
                ],
                model=self.llm_name,
                temperature=0,
            )
            return chat_completion.choices[0].message.content
        response = self.get_llm(self.llm_name).invoke(prompt_content)
        content = getattr(response, "content", response)
        if not isinstance(content, str):
            raise TypeError("Chat model returned non-text JSON repair output")
        return content


    def get_vectordb(self, normal_log_entries):
        if self.embedding_backend == "openai":
            embedding = OpenAIEmbeddings(
                model=self.embedding_model,
                api_key=self.api_key,
                base_url=self.api_base,
            )
        elif self.embedding_backend == "huggingface":
            embedding = HuggingFaceEmbeddings(
                model_name=self.embedding_model,
                model_kwargs={"device": self.embedding_device},
                encode_kwargs={"normalize_embeddings": True},
            )
        else:
            raise ValueError(
                f"Unsupported LogRAG embedding backend: "
                f"{self.embedding_backend}"
            )
        self.model_activity["embedded_documents"] = len(normal_log_entries)
        # 读取训练数据
        if not os.path.exists(self.persist_directory):
            os.mkdir(self.persist_directory)
            
        if not os.listdir(self.persist_directory):
            # 保存到硬盘
            self.logger.info('Using embedding...')
            vectordb = Chroma.from_texts(
                texts=normal_log_entries,
                embedding=embedding,
                persist_directory=self.persist_directory
            )
        else:
            # 从硬盘load
            self.logger.info('Loading from db...')
            if self.prompt == "prompt1" or self.prompt == "prompt2":
                self.persist_directory = "db/none"
            
            vectordb = Chroma(
                persist_directory=self.persist_directory, 
                embedding_function=embedding
            )
        return vectordb
    
    def get_retriever(self, retriever_type='thr', vectordb='None'):
        if retriever_type == "mmr":
            retriever = vectordb.as_retriever(
                        search_type="mmr", 
                        search_kwargs={"k": 5}
                    )
        elif retriever_type == "thr":
            if self.prompt == "prompt3":
                self.topk = 1
            else:
                self.topk = 5
            retriever = vectordb.as_retriever(
                        search_type="similarity_score_threshold", 
                        search_kwargs={"score_threshold": self.threshold, "k":self.topk}
                    )
        return retriever

    def get_local_llm(self, model_path):
        
        self.logger.info(f"Loading model: {model_path}")
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"

        # model = AutoModelForCausalLM.from_pretrained(model_path)

        gc.collect()
        torch.cuda.empty_cache()

        model = AutoModelForCausalLM.from_pretrained(model_path).to(self.device)

        text_generation_pipeline = pipeline(
            model=model,
            tokenizer=tokenizer,
            task="text-generation",
            # do_sample=True,
            temperature=0,
            repetition_penalty=1.1,
            pad_token_id=2,
            return_full_text=True,
            max_new_tokens=1000,
        )

        mistral_llm = HuggingFacePipeline(pipeline=text_generation_pipeline)

        return mistral_llm


    def get_normal_log_entries(self):
        # get normal log entries from self.train_data_path
        train_df = pd.read_csv(self.train_data_path)
        train_df = train_df[train_df['Label'] == '-']
        normal_log_entries = train_df['EventTemplate'].unique().tolist()
        return normal_log_entries

    def post_process(self, anomaly_logs_path, test_data_path):
        os.makedirs(self.output_dir, exist_ok=True)
        result_path = os.path.join(
            self.output_dir, 'anomaly_logs_detc_by_rag.csv'
        )
        answer_path = os.path.join(self.output_dir, 'llm_answer.json')
        
        QA_CHAIN_PROMPT = PromptTemplate.from_template(template=self.prompt)
        normal_log_entries = self.get_normal_log_entries()
        self.logger.info(f"Normal log templates to embedding: , {len(normal_log_entries)}")
        vector_db = self.get_vectordb(normal_log_entries)
        retriever = self.get_retriever("thr", vector_db)
        qa_chain = RetrievalQA.from_chain_type(
                        self.get_llm(self.llm_name),
                        chain_type='stuff',
                        retriever= retriever,
                        return_source_documents=True,
                        # verbose=True,
                        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
                    )
        pos_df = pd.read_csv(anomaly_logs_path)
        test_df = pd.read_csv(test_data_path)
 
        # 将Template按照数量从多到少排序，先看数据量多的
        pos_event_template_counts = pos_df['EventTemplate'].value_counts().to_dict()
        test_event_template_counts = test_df['EventTemplate'].value_counts().to_dict()
        pos_log_templates  = list(pos_event_template_counts.keys())

        df_result = pd.DataFrame(columns=['is_anomaly', f'frequency_inpos', 'frequency_intest', 'EventTemplate', 'reason', 'topk_similary_log_list'])

        answer_list = []
        
        for test_log in tqdm(pos_log_templates):

            self.model_activity["chat_queries"] += 1
            answer = qa_chain.invoke({"query": test_log})
            # 提取每个Document对象的page_content
            answer['source_documents'] = [doc.page_content for doc in answer['source_documents']]
            
            topk_similary_log_list = answer['source_documents']
            answer_list.append(answer)
            
            content = answer['result']
            try:
                result = self._parse_json_object(content)
            except ValueError as error:
                self.logger.info('---begin---')
                self.logger.info(error)
                self.logger.info(content)
                self.logger.info('---end-----')
                prompt = "Please keep only the Json part of the following content, and fill the is_anomaly into the \'is_anomaly\', \
                fill the reason into the \'reason\' field of the json. The returned content only needs a string in json format, Input:\n\n"
                prompt_content = prompt + content      
                content = self.ask_ChatGPT(prompt_content)
                self.logger.info("regenerate: "  + content)
                result = self._parse_json_object(content)
            # 提取is_anomaly和reason
            is_anomaly = result['is_anomaly']
            try:
                reason = result['reason']
            except:
                reason = "None"
            # 将数据追加到DataFrame
            df_result = pd.concat([ df_result, 
                                    pd.DataFrame({
                                        'is_anomaly':[is_anomaly],
                                        'frequency_inpos':[int(pos_event_template_counts[test_log])],
                                        'frequency_intest':[int(test_event_template_counts[test_log])],
                                        'EventTemplate': [test_log], 
                                        'reason': [reason],
                                        'topk_similary_log_list': [topk_similary_log_list]
                                        })
                                ], ignore_index=True)
            
            df_result.to_csv(result_path, index=False)
        df_result.to_csv(result_path, index=False)

        with open(answer_path, 'w') as file:
            json.dump(answer_list, file)

        with open(
            os.path.join(self.output_dir, 'model_activity.json'),
            'w',
            encoding='utf-8',
        ) as file:
            json.dump(self.model_activity, file, indent=2)
            
        self.logger.info(f'Saved results to \n{result_path}\n{answer_path}')
        
        anomaly_templates = df_result[df_result['is_anomaly'] == 1]['EventTemplate']
        filtered_df = pos_df[pos_df['EventTemplate'].isin(anomaly_templates)]
        return filtered_df['LineId'].tolist()
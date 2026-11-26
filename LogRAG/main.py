import numpy as np
import pandas as pd
import os
import logging
from prelogad.DeepSVDD.src.deepSVDD import DeepSVDD
from prelogad.DeepSVDD.src.datasets.main import load_dataset
from tqdm import tqdm 
import logging
from postprocess import RAG
import yaml
from utils.evaluator import evaluate
import torch
from pathlib import Path

with open('config.yaml', 'r') as file:
    configs = yaml.safe_load(file)

api_key = (
    os.environ.get("OPENAI_API_KEY") or configs.get("api_key", "")
).strip()
api_base = (
    os.environ.get("OPENAI_BASE_URL")
    or os.environ.get("OPENAI_API_BASE")
    or configs.get("api_base")
    or "https://api.openai.com/v1"
)
configs["api_key"] = api_key
configs["api_base"] = api_base
configs["llm_name"] = os.environ.get(
    "LOGRAG_CHAT_MODEL", configs.get("llm_name", "gpt-3.5-turbo")
)
configs["embedding_model"] = os.environ.get(
    "LOGRAG_EMBEDDING_MODEL",
    configs.get("embedding_model", "text-embedding-ada-002"),
)
configs["llm_backend"] = os.environ.get(
    "LOGRAG_LLM_BACKEND", configs.get("llm_backend", "openai")
)
configs["embedding_backend"] = os.environ.get(
    "LOGRAG_EMBEDDING_BACKEND",
    configs.get("embedding_backend", "openai"),
)
configs["embedding_device"] = os.environ.get(
    "LOGRAG_EMBEDDING_DEVICE",
    configs.get("embedding_device", "cpu"),
)
configs["ollama_base_url"] = os.environ.get(
    "OLLAMA_BASE_URL",
    configs.get("ollama_base_url", "http://127.0.0.1:11434"),
)
configs["ollama_num_ctx"] = int(
    os.environ.get(
        "LOGRAG_OLLAMA_NUM_CTX",
        configs.get("ollama_num_ctx", 4096),
    )
)
configs["ollama_num_predict"] = int(
    os.environ.get(
        "LOGRAG_OLLAMA_NUM_PREDICT",
        configs.get("ollama_num_predict", 512),
    )
)
configs["log_structed_path"] = os.environ.get(
    "LOGRAG_STRUCTURED_CSV", configs["log_structed_path"]
)
configs["encoder_path"] = os.environ.get(
    "LOGRAG_ENCODER_PATH", configs["encoder_path"]
)
configs["protocol_dir"] = os.environ.get(
    "LOGRAG_PROTOCOL_DIR", configs.get("protocol_dir", "")
)
configs["shared_output_dir"] = os.environ.get(
    "LOGRAG_SHARED_OUTPUT_DIR",
    configs.get("shared_output_dir", "./output/shared_benchmark_v1"),
)
configs["output_dir"] = os.environ.get(
    "LOGRAG_OUTPUT_DIR", configs.get("output_dir", "./output")
)
configs["dataset_name"] = os.environ.get(
    "LOGRAG_DATASET", configs.get("dataset_name", "BGL")
)
configs["persist_directory"] = os.environ.get(
    "LOGRAG_PERSIST_DIRECTORY",
    configs.get("persist_directory", "./output/ragdb-bgl"),
)
configs["embedding_batch_size"] = int(
    os.environ.get(
        "LOGRAG_EMBEDDING_BATCH_SIZE",
        configs.get("embedding_batch_size", 64),
    )
)
configs["seed"] = int(os.environ.get("LOGRAG_SEED", configs.get("seed", 42)))
configs["n_epochs"] = int(
    os.environ.get("LOGRAG_EPOCHS", configs.get("n_epochs", 150))
)
configs["batch_size"] = int(
    os.environ.get("LOGRAG_BATCH_SIZE", configs.get("batch_size", 40960))
)

if configs.get("is_rag", False):
    if configs["llm_backend"] not in {"openai", "ollama", "transformers"}:
        raise ValueError(
            f"Unsupported LogRAG chat backend: {configs['llm_backend']}"
        )
    if configs["embedding_backend"] not in {"openai", "huggingface"}:
        raise ValueError(
            "Unsupported LogRAG embedding backend: "
            f"{configs['embedding_backend']}"
        )
    if (
        configs["llm_backend"] == "openai"
        or configs["embedding_backend"] == "openai"
    ):
        if not api_key or api_key == "PUT_YOUR_OWN_API_KEY_HERE":
            raise RuntimeError(
                "The selected OpenAI chat/embedding backend requires "
                "OPENAI_API_KEY. Add it as a Kaggle Secret; do not store the "
                "key in config.yaml."
            )
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_API_BASE"] = api_base
        os.environ["OPENAI_BASE_URL"] = api_base
    if configs["llm_backend"] == "ollama":
        os.environ["OLLAMA_HOST"] = configs["ollama_base_url"].removeprefix(
            "http://"
        ).removeprefix("https://")

output_dir = Path(configs["output_dir"])
output_dir.mkdir(parents=True, exist_ok=True)
    
# set logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(output_dir / 'runtime.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def train_deepsvdd(train_data_path):
    output_dir.mkdir(parents=True, exist_ok=True)
    
    deep_SVDD = DeepSVDD('soft-boundary')
    deep_SVDD.set_network("mlp")
    
    if not configs['is_train']:
        deep_SVDD.load_model(
            model_path=str(output_dir / 'model.tar'), load_ae=False
        )
        logger.info('Loading model from %s', output_dir / 'model.tar')
    else :
        # dataloader 
        train_dataset = load_dataset(
            data_path=train_data_path,
            encoder_path=configs['encoder_path'],
            device=configs['device'],
            batch_size=configs.get('embedding_batch_size', 64),
        )
        # pretrain and train 
        if configs['is_pretrain']:
            deep_SVDD.pretrain( train_dataset,
                                optimizer_name=configs['optimizer_name'],
                                lr=configs['lr'],
                                n_epochs=configs['n_epochs'],
                                lr_milestones=configs['lr_milestones'],
                                batch_size=configs['batch_size'],
                                weight_decay=configs['weight_decay'],
                                device=configs['device'],
                                n_jobs_dataloader=configs['n_jobs_dataloader'])
        deep_SVDD.train(train_dataset,
                        optimizer_name=configs['optimizer_name'],  
                        lr=configs['lr'],  
                        n_epochs=configs['n_epochs'],  
                        lr_milestones=configs['lr_milestones'],  
                        batch_size=configs['batch_size'],  
                        weight_decay=configs['weight_decay'],  
                        device=configs['device'],  
                        n_jobs_dataloader=configs['n_jobs_dataloader'])  
    # Save results, model, and configuration
    model_path = output_dir / 'model.tar'
    deep_SVDD.save_results(export_json=str(output_dir / 'results.json'))
    deep_SVDD.save_model(export_model=str(model_path), save_ae=False)
    return str(model_path)

def anomaly_detection(model_path, test_data_path):
    logger.info("start testing....")
    
    deep_SVDD = DeepSVDD('soft-boundary')
    deep_SVDD.set_network("mlp")
    deep_SVDD.load_model(model_path=model_path, load_ae=False)
    logger.info('Loading model from %s', model_path)
    
    test_dataset = load_dataset(
        data_path=test_data_path,
        encoder_path=configs['encoder_path'],
        device=configs['device'],
        batch_size=configs.get('embedding_batch_size', 64),
    )
    anomalys, _ = deep_SVDD.test(
        test_dataset,
        device=configs['device'],
        n_jobs_dataloader=configs['n_jobs_dataloader'],
    )

    anomaly_lineid_list = [item[0] for item in tqdm(anomalys, desc='saving anomaly LineIds to list')]
   
    output_file = output_dir / 'anomaly_logs_detc_by_svdd.csv'
    # 保存deepsvdd检测为异常的
    df_test = pd.read_csv(test_data_path)
    
    pos_df = df_test[df_test["LineId"].isin(anomaly_lineid_list)]
    pos_df.to_csv(output_file, index=False)
    
    return output_file, anomaly_lineid_list


def main():
    logger.info({
        key: "***" if key == "api_key" and value else value
        for key, value in configs.items()
    })
    all_df = pd.read_csv(configs['log_structed_path'])
    num_train = int(configs['train_ratio']*len(all_df))

    train_df = all_df[:num_train]
    train_df = train_df[train_df['Label'] == '-']
    test_df = all_df[num_train:]
    
    
    train_log_structed_path = f"./dataset/{configs['dataset_name']}/train_log_structured.csv"
    test_log_structed_path = f"./dataset/{configs['dataset_name']}/test_log_structured.csv"
    os.makedirs(os.path.dirname(train_log_structed_path), exist_ok=True)

    train_df.to_csv(train_log_structed_path, index=False)
    test_df.to_csv(test_log_structed_path, index=False)
    
    # train deepsvdd, get log token embeddings
    model_path = train_deepsvdd(train_log_structed_path)
    # do anomaly detection
    anomaly_logs_path, anomaly_lineid_list = anomaly_detection(model_path, test_log_structed_path)
    
    # rag postporcessing, get log templates embeddings
    if configs['is_rag']:
        RagPoster = RAG.RAGPostProcessor(configs, train_data_path=train_log_structed_path, logger=logger)
        anomaly_lineid_list = RagPoster.post_process(anomaly_logs_path, test_log_structed_path)
    # print final results
    evaluate(configs, test_log_structed_path, anomaly_lineid_list, logger)
    

if __name__ == '__main__':
    main()
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from postprocess import RAG


class RAGBackendTests(unittest.TestCase):
    def test_ollama_chat_uses_configured_model_and_server(self):
        processor = object.__new__(RAG.RAGPostProcessor)
        processor.llm_backend = "ollama"
        processor.ollama_base_url = "http://127.0.0.1:11434"
        processor.ollama_num_ctx = 4096
        processor.ollama_num_predict = 512

        with patch("postprocess.RAG.ChatOllama") as chat_ollama:
            result = processor.get_llm(
                "hf.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF:Q4_K_M"
            )

        chat_ollama.assert_called_once_with(
            model="hf.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF:Q4_K_M",
            base_url="http://127.0.0.1:11434",
            temperature=0,
            num_ctx=4096,
            num_predict=512,
        )
        self.assertIs(result, chat_ollama.return_value)

    def test_huggingface_embedding_backend_does_not_use_openai(self):
        processor = object.__new__(RAG.RAGPostProcessor)
        processor.embedding_backend = "huggingface"
        processor.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        processor.embedding_device = "cpu"
        processor.model_activity = {"embedded_documents": 0}
        processor.persist_directory = ""
        processor.prompt = "prompt5"
        processor.logger = Mock()

        with tempfile.TemporaryDirectory() as temporary_directory:
            processor.persist_directory = str(
                Path(temporary_directory) / "ragdb"
            )
            with (
                patch("postprocess.RAG.HuggingFaceEmbeddings") as embeddings,
                patch(
                    "postprocess.RAG.Chroma.from_texts",
                    return_value=object(),
                ) as from_texts,
                patch("postprocess.RAG.OpenAIEmbeddings") as openai_embeddings,
            ):
                processor.get_vectordb(["normal template"])

        embeddings.assert_called_once_with(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        openai_embeddings.assert_not_called()
        self.assertEqual(processor.model_activity["embedded_documents"], 1)
        self.assertEqual(from_texts.call_args.kwargs["texts"], ["normal template"])


if __name__ == "__main__":
    unittest.main()

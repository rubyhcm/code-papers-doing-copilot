
from prelogad.DeepSVDD.src.base.torchvision_dataset import TorchvisionDataset
from prelogad.DeepSVDD.src.datasets.vocab import Vocab
import pandas as pd 
import torch
import numpy as np
import json
from tqdm import tqdm
from tqdm import tqdm
# import tensorflow as tf
from transformers import AutoTokenizer
from transformers import BertModel
import torch
import re
import pickle
import string
from torch.utils.data import Dataset

def read_json(filename):
    with open(filename, 'r') as load_f:
        file_dict = json.load(load_f)
    return file_dict

# version 2 use log tokens

def bert_encoder(s,  biglog_tokenizer, pretrained_model, no_wordpiece=0):
    """ Compute semantic vector with BERT
    Parameters
    ----------
    s: string to encode
    no_wordpiece: 1 if you do not use sub-word tokenization, otherwise 0

    Returns
    -------
        np array in shape of (768,)
    """
    if no_wordpiece:
        words = s.split(" ")
        words = [word for word in words if word in biglog_tokenizer.vocab.keys()]
        s = " ".join(words)
    tokenized_data = biglog_tokenizer(
        s, padding="longest", truncation=True, max_length=150, return_tensors="pt"
    )
    with torch.inference_mode():
        outputs = pretrained_model(
            input_ids=tokenized_data["input_ids"],
            attention_mask=tokenized_data["attention_mask"],
        )
    mask = tokenized_data["attention_mask"].unsqueeze(-1)
    return (outputs.last_hidden_state * mask).sum(dim=1)[0] / mask.sum(dim=1)[0]

def clean(s):
    """ Preprocess log message
    Parameters
    ----------
    s: str, raw log message

    Returns
    -------
    str, preprocessed log message without number tokens and special characters
    """
    # s = re.sub(r'(\d+\.){3}\d+(:\d+)?', " ", s)
    # s = re.sub(r'(\/.*?\.[\S:]+)', ' ', s)
    s = re.sub('\]|\[|\)|\(|\=|\,|\;', ' ', s)
    s = " ".join([word.lower() if word.isupper() else word for word in s.strip().split()])
    s = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', s))
    s = " ".join([word for word in s.split() if not bool(re.search(r'\d', word))])
    trantab = str.maketrans(dict.fromkeys(list(string.punctuation)))
    content = s.translate(trantab)
    s = " ".join([word.lower().strip() for word in content.strip().split()])
    return s



def _binary_label(value):
    if isinstance(value, (int, np.integer, float, np.floating)):
        if value in (0, 1):
            return int(value)
        raise ValueError(f"Expected binary label, got {value!r}")

    label = str(value).strip().lower()
    if label in {"-", "normal", "success", "0"}:
        return 0
    if label in {"anomaly", "fail", "1"}:
        return 1
    raise ValueError(f"Unknown log label: {value!r}")


class _EncodedRows(Dataset):
    def __init__(self, embeddings, vector_ids, labels, line_ids):
        self.embeddings = embeddings
        self.vector_ids = vector_ids
        self.labels = labels
        self.line_ids = line_ids

    def __len__(self):
        return len(self.vector_ids)

    def __getitem__(self, index):
        embedding = torch.from_numpy(
            self.embeddings[self.vector_ids[index]].copy()
        )
        return (
            embedding,
            torch.tensor(self.labels[index], dtype=torch.long),
            torch.tensor(self.line_ids[index], dtype=torch.long),
        )


class BGL_Dataset(TorchvisionDataset):
    def __init__(
        self,
        root: str,
        encoder_path: str,
        device: str = "cpu",
        batch_size: int = 64,
    ):
        '''
            root: data_path
        '''
        if batch_size < 1:
            raise ValueError("Embedding batch size must be positive")
        if device.startswith("cuda") and not torch.cuda.is_available():
            raise RuntimeError(f"CUDA was requested but is unavailable: {device}")

        frame = pd.read_csv(root, usecols=["LineId", "Label", "Content"])
        if frame.empty:
            raise ValueError(f"Dataset is empty: {root}")

        cleaned = frame["Content"].fillna("").map(
            lambda value: clean(str(value))
        )
        vector_ids, unique_contents = pd.factorize(cleaned, sort=False)
        labels = np.asarray(
            [_binary_label(value) for value in frame["Label"]],
            dtype=np.int64,
        )
        line_ids = pd.to_numeric(frame["LineId"], errors="raise").to_numpy(
            dtype=np.int64
        )
        del frame, cleaned

        biglog_tokenizer = AutoTokenizer.from_pretrained(encoder_path)
        pretrained_model = BertModel.from_pretrained(encoder_path).to(device)
        pretrained_model.eval()

        embedding_batches = []
        for start in tqdm(
            range(0, len(unique_contents), batch_size),
            desc="Encoding unique log messages",
        ):
            texts = [
                str(text)
                for text in unique_contents[start:start + batch_size]
            ]
            tokenized = biglog_tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=150,
                return_tensors="pt",
            )
            tokenized = {
                key: value.to(device) for key, value in tokenized.items()
            }
            with torch.inference_mode():
                hidden = pretrained_model(**tokenized).last_hidden_state
                mask = tokenized["attention_mask"].unsqueeze(-1)
                vectors = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp_min(1)
            embedding_batches.append(vectors.cpu().numpy().astype(np.float32))

        embeddings = np.concatenate(embedding_batches, axis=0)
        vector_ids = np.asarray(vector_ids, dtype=np.int32)
        normal_rows = labels == 0

        self.train_set = _EncodedRows(
            embeddings,
            vector_ids[normal_rows],
            labels[normal_rows],
            line_ids[normal_rows],
        )
        self.test_set = _EncodedRows(
            embeddings,
            vector_ids,
            labels,
            line_ids,
        )


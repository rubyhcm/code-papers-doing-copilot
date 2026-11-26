import numpy as np
from torch.utils.data import Dataset
import math

EMBEDDING_DIM = 768


class DataGenerator(Dataset):
    def __init__(self, x, y, window_size, embedding_matrix=None):
        'Initialization'
        self.x = x
        self.y = y
        self.window_size = window_size
        self.embedding_matrix = embedding_matrix
        if embedding_matrix is not None:
            if x.ndim != 2:
                raise ValueError("Template-ID sequences must have shape [samples, sequence]")
            if embedding_matrix.ndim != 2 or embedding_matrix.shape[1] != EMBEDDING_DIM:
                raise ValueError(
                    f"Embedding matrix must have shape [templates, {EMBEDDING_DIM}]"
                )
            if x.size and (x.min() < 0 or x.max() >= len(embedding_matrix)):
                raise ValueError("Template ID is outside the embedding matrix")

    def __len__(self):
        'Denotes the number of batches'
        return math.ceil(len(self.x))

    def __getitem__(self, index):
        'Generate one batch of data'
        # x = self.x[index * self.batch_size:(index + 1) * self.batch_size]
        # y = self.y[index * self.batch_size:(index + 1) * self.batch_size]
        x = self.x[index]
        y = self.y[index]
        if self.embedding_matrix is not None:
            x = self.embedding_matrix[x]

        # 最大设置为40暂定不需要最大number的
        num_tokens = x.shape[0]
        # print('x.shape[0]:', num_tokens)

        mix_num_boxes = min(int(num_tokens), self.window_size)
        # # mix_boxes_pad = np.zeros((self._max_region_num, 5))
        mix_features_pad = np.zeros((self.window_size, EMBEDDING_DIM), dtype=np.float32)
        mix_features_pad[:mix_num_boxes] = x[:mix_num_boxes]
        x = mix_features_pad
        # print(x.shape)
        # x = pad_sequence([torch.from_numpy(np.array(x)) for x in input_x], batch_first=True).float()
        # print('x 类型：',type(x))
        return x, y

import torch
from torch.utils.data import DataLoader
from torch.utils.data import Dataset
from transformers import BertTokenizer


def load_data(data,
              batch_size,
              max_len=64,
              train=True,
              tokenizer_config='bert-base-cased'):
    return DataLoader(
        dataset=OieEvalDataset(
            data,
            max_len,
            tokenizer_config),
        batch_size=batch_size,
        num_workers=4,
        pin_memory=True)



class OieEvalDataset(Dataset):
    def __init__(self, data, max_len, tokenizer_config='bert-base-cased'):
        self.sentences = data
        self.tokenizer = BertTokenizer.from_pretrained(tokenizer_config)
        self.vocab = self.tokenizer.vocab
        self.max_len = max_len

        self.pad_idx = self.vocab['[PAD]']
        self.cls_idx = self.vocab['[CLS]']
        self.sep_idx = self.vocab['[SEP]']
        self.mask_idx = self.vocab['[MASK]']
        
    def add_pad(self, token_ids):
        diff = self.max_len - len(token_ids)
        if diff > 0:
            token_ids += [self.pad_idx] * diff
        else:
            token_ids = token_ids[:self.max_len-1] + [self.sep_idx]
        return token_ids

    def idx2mask(self, token_ids):
        return [token_id != self.pad_idx for token_id in token_ids]

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, idx):
        token_ids = self.add_pad(self.tokenizer.encode(self.sentences[idx]))
        att_mask = self.idx2mask(token_ids)
        token_strs = self.tokenizer.convert_ids_to_tokens(token_ids)
        sentence = self.sentences[idx]

        assert len(token_ids) == self.max_len
        assert len(att_mask) == self.max_len
        assert len(token_strs) == self.max_len
        batch = [
            torch.tensor(token_ids),
            torch.tensor(att_mask),
            token_strs,
            sentence
        ]
        return batch


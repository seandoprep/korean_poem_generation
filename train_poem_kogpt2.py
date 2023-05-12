import torch
import transformers
from transformers import AutoModelWithLMHead, PreTrainedTokenizerFast
from fastai.text.all import *
import re
import fastai
import pandas as pd

#download model and tokenizer
tokenizer = PreTrainedTokenizerFast.from_pretrained("skt/kogpt2-base-v2",
  bos_token='</s>', eos_token='</s>', unk_token='<unk>',
  pad_token='<pad>', mask_token='<mask>')
model = AutoModelWithLMHead.from_pretrained("skt/kogpt2-base-v2")

added_token_num = tokenizer.add_tokens('/n', '\n')
model.resize_token_embeddings(tokenizer.vocab_size + added_token_num)

# Prepare Huggingface
REPO_NAME = 'KoGPT2_poem_finetuning_full'  # REPO_NAME(저장할 파일 명) 구분할 수 있게 수정해주기
AUTH_TOKEN = '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'

# Prepare data
data_path = './data/poem_love_crawled_final.xlsx'
data = pd.read_excel(data_path)
data_list = list(data['content'])

with open('poemlove.txt', 'w', encoding='UTF-8') as f:
    for poem in data_list:
      print(poem)
      f.write(poem + '\n')

with open('poemlove.txt','r', -1, "utf-8") as f:
    lines = f.read()

lines=" ".join(lines.split())

#model input output tokenizer
class TransformersTokenizer(Transform):
    def __init__(self, tokenizer): self.tokenizer = tokenizer
    def encodes(self, x):
        toks = self.tokenizer.tokenize(x)
        return tensor(self.tokenizer.convert_tokens_to_ids(toks))
    def decodes(self, x): return TitledStr(self.tokenizer.decode(x.cpu().numpy()))

#split data
train=lines[:int(len(lines)*0.9)]
test=lines[int(len(lines)*0.9): int(len(lines))]
splits = [[0],[1]]

#init dataloader
tls = TfmdLists([train,test], TransformersTokenizer(tokenizer), splits=splits, dl_type=LMDataLoader)
batch,seq_len = 16, 256
dls = tls.dataloaders(bs=batch, seq_len=seq_len)
# dls.show_batch(max_n=2)

# gpt2 ouput is tuple, we need just one val
class DropOutput(Callback):
    def after_pred(self): self.learn.pred = self.pred[0]

learn = Learner(dls, model, loss_func=CrossEntropyLossFlat(), cbs=[DropOutput], metrics=Perplexity()).to_fp16()
lr = learn.lr_find()
learn.fine_tune(10)

model.push_to_hub(REPO_NAME,
                  use_temp_dir=True,
                  use_auth_token=AUTH_TOKEN
                  )
tokenizer.push_to_hub(REPO_NAME,
                  use_temp_dir=True,
                  use_auth_token=AUTH_TOKEN
                  )





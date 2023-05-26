import torch
import transformers
from transformers import AutoModelWithLMHead, PreTrainedTokenizerFast
from fastai.text.all import *
import re
import fastai
import pandas as pd


def train(args):

    #download model and tokenizer
    tokenizer = PreTrainedTokenizerFast.from_pretrained(
        args.model_name_or_path,
        bos_token='</s>',
        eos_token='</s>',
        unk_token='<unk>',
        pad_token='<pad>',
        mask_token='<mask>')
    model = AutoModelWithLMHead.from_pretrained(args.model_name_or_path)
    added_token_num = tokenizer.add_tokens('/n', '\n')
    model.resize_token_embeddings(tokenizer.vocab_size + added_token_num)

    # Prepare Huggingface
    REPO_NAME = args.repo_name 
    AUTH_TOKEN = args.auth_token

    # Prepare data
    data_path = os.path.join(args.data_dir, args.train_filename)
    data = pd.read_excel(data_path)
    data_list = list(data['content'])

    with open(args.data_dir + 'poem.txt', 'w', encoding='UTF-8') as f:
        for poem in data_list:
          try:  
            f.write(poem + '\n')
          except:
            pass

    with open(args.data_dir + 'poem.txt','r', -1, "utf-8") as f:
        lines = f.read()

    lines = " ".join(lines.split())

    #model input output tokenizer
    class TransformersTokenizer(Transform):
        def __init__(self, tokenizer): self.tokenizer = tokenizer
        def encodes(self, x):
            toks = self.tokenizer.tokenize(x)
            return tensor(self.tokenizer.convert_tokens_to_ids(toks))
        def decodes(self, x): return TitledStr(self.tokenizer.decode(x.cpu().numpy()))

    #split data
    train = lines[:int(len(lines)*args.data_split_ratio)]
    test = lines[int(len(lines)*args.data_split_ratio): int(len(lines))]
    splits = [[0],[1]]

    #init dataloader
    tls = TfmdLists([train,test], TransformersTokenizer(tokenizer), splits=splits, dl_type=LMDataLoader)
    batch,seq_len = args.batch_size, args.seq_len
    dls = tls.dataloaders(bs=batch, seq_len=seq_len)
    
    # gpt2 ouput is tuple, we need just one val
    class DropOutput(Callback):
        def after_pred(self): self.learn.pred = self.pred[0]

    learn = Learner(dls, model, loss_func=CrossEntropyLossFlat(), cbs=[DropOutput], metrics=Perplexity()).to_fp16()
    learn.remove_cb(ProgressCallback)
    lr = learn.lr_find()
    learn.fine_tune(args.num_train_epochs)

    model.push_to_hub(REPO_NAME,
                      use_temp_dir=True,
                      use_auth_token=AUTH_TOKEN
                      )
    tokenizer.push_to_hub(REPO_NAME,
                      use_temp_dir=True,
                      use_auth_token=AUTH_TOKEN
                      )



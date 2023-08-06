# -*- coding = utf-8 -*-
# @time: 2022/3/1 1:37 下午
# @Author: erazhan
# @File: main_mitc.py

# ----------------------------------------------------------------------------------------------------------------------
import os
import copy

from transformers import BertTokenizer

from erazhan_utils import read_json_file

from erazhan_algorithms.MITC import train_mitc, eval_mitc, get_mitc_params_help, init_mitc_model
from erazhan_algorithms.MITC import get_mitc_parser
from erazhan_algorithms import MITC_DEFAULT_PARAM_DICT, MITC_OTHER_PARAM_DICT

intent_vocab = ["身高", "体重", "发烧", "既往史", "手术史", "过敏史"]

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

MITC_DEFAULT_PARAM_DICT = {"gpu": 0,
                           "maxlen": 256,
                           "batch_size": 32,
                           "predict_batch_size": 4,
                           "learning_rate": 2e-5,
                           "warmup_proportion": 0.1,
                           "epochs": 50,
                           "save_steps": 500,
                           "print_steps": 20,
                           "disable": False}

MITC_OTHER_PARAM_DICT = {"bert_model": "/home/zhanjiyuan/code/pretrained_model/chinese-roberta-wwm-ext",
                         "train_file": "./data/test_train_mitc_50.json",
                         "eval_file": "./data/test_train_mitc_50.json",
                         "output_dir": "./model",
                         "predict_dir": "./model",
                         "mitc_intents": intent_vocab,
                         "mitc_num_labels": len(intent_vocab),
                         }

def train_or_eval_from_eralgo(mode = "train"):

    param_dict = copy.deepcopy(MITC_DEFAULT_PARAM_DICT)
    param_dict.update(MITC_OTHER_PARAM_DICT)

    mitc_args = get_mitc_parser(param_dict)
    tokenizer = BertTokenizer.from_pretrained(mitc_args.bert_model)

    train_data = read_json_file(param_dict["train_file"])
    eval_data = read_json_file(param_dict["eval_file"])

    train_text,train_intents,train_intent_labels,eval_text,eval_intents,eval_intent_labels = [],[],[],[],[],[]

    for one_data in train_data:
        train_text.append(one_data["text"])
        train_intents.append(one_data["intents"])
        train_intent_labels.append(one_data["intent_labels"])

    for one_data in eval_data:
        eval_text.append(one_data["text"])
        eval_intents.append(one_data["intents"])
        eval_intent_labels.append(one_data["intent_labels"])

    # return
    if mode == "train":
        kwargs = {"args": mitc_args,
                  "intent_vocab": intent_vocab,
                  "train_text": train_text,
                  "eval_text": eval_text,
                  "train_label": train_intents,
                  "eval_label": eval_intents,
                  "tokenizer": tokenizer}
        train_mitc(**kwargs)
    elif mode == "eval" or mode == "test":
        eval_kwargs = {"args": mitc_args, "tokenizer": tokenizer, "intent_vocab": intent_vocab}
        model = init_mitc_model(mitc_args, from_scratch = False)
        eval_mitc(model, text_list = eval_text, label_list = eval_intent_labels, **eval_kwargs)
    else:
        pass

if __name__ == "__main__":

    get_mitc_params_help()
    train_or_eval_from_eralgo(mode="train")

    pass

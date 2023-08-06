# -*- coding = utf-8 -*-
# @time: 2022/2/24 3:14 下午
# @Author: erazhan
# @File: main_tc.py

# ----------------------------------------------------------------------------------------------------------------------
import copy

from transformers import BertTokenizer

from erazhan_utils import read_json_file
from erazhan_algorithms.TC import train_tc, eval_tc, get_tc_params_help,init_tc_model
from erazhan_algorithms.TC import get_tc_parser
from erazhan_algorithms import TC_DEFAULT_PARAM_DICT, TC_OTHER_PARAM_DICT

tc_intents = ["其它", "身高体重"]

TC_DEFAULT_PARAM_DICT = {
    "gpu":0,
    "maxlen":256,
    "batch_size":32,
    "predict_batch_size":4,
    "learning_rate":2e-05,
    "warmup_proportion":0.1,
    "epochs":5,
    "save_steps":500,
    "print_steps":20,
    "disable":False
}

TC_OTHER_PARAM_DICT =  {
    "bert_model": "/home/zhanjiyuan/code/pretrained_model/chinese-roberta-wwm-ext",
    "train_file": "./data/train_ks_ea.json",
    "eval_file": "./data/eval_ks_ea.json",
    "output_dir": "./model_tc",
    "predict_dir": "./model_tc",
    "tc_intents": tc_intents,
    "tc_num_labels": len(tc_intents)
}

def train_or_eval_from_eralgo(mode = "train"):

    param_dict = copy.deepcopy(TC_DEFAULT_PARAM_DICT)
    param_dict.update(TC_OTHER_PARAM_DICT)

    tc_args = get_tc_parser(param_dict)
    tokenizer = BertTokenizer.from_pretrained(tc_args.bert_model)

    train_data = read_json_file(param_dict["train_file"])
    eval_data = read_json_file(param_dict["eval_file"])

    train_text,train_label,eval_text,eval_label = [],[],[],[]

    for one_data in train_data:
        train_text.append(one_data["text"])
        train_label.append(one_data["label"])

    for one_data in eval_data:
        eval_text.append(one_data["text"])
        eval_label.append(one_data["label"])

    if mode == "train":
        kwargs = {"args": tc_args,
              "train_text": train_text,
              "eval_text": eval_text,
              "train_label": train_label,
              "eval_label": eval_label,
              "tokenizer": tokenizer}
        train_tc(**kwargs)
    elif mode == "eval" or mode == "test":
        eval_kwargs = {"args": tc_args, "tokenizer": tokenizer}
        model = init_tc_model(tc_args, from_scratch=False)
        eval_tc(model, text_list = eval_text, label_list = eval_label,**eval_kwargs)
    else:
        pass

if __name__ == "__main__":

    get_tc_params_help()
    train_or_eval_from_eralgo(mode="eval")

    pass
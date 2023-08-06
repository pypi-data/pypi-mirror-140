# -*- coding = utf-8 -*-
# @time: 2022/2/28 11:30 上午
# @Author: erazhan
# @File: predict.py

# ----------------------------------------------------------------------------------------------------------------------
from tqdm import tqdm
import torch
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
from transformers import BertTokenizer

from .data import convert_to_inputdata_mitc, trans_inputdata_mitc, recover_intent
from .models import init_mitc_model

def predict_on_batch_mitc(model, text_list, **kwargs):

    '''tokenizer'''
    assert "args" in kwargs.keys() and "intent_vocab" in kwargs.keys()

    intent_vocab = kwargs["intent_vocab"]
    args = kwargs["args"]
    maxlen = args.maxlen

    tokenizer = BertTokenizer.from_pretrained(args.bert_model) if "tokenizer" not in kwargs.keys() else kwargs["tokenizer"]

    InputData_list = convert_to_inputdata_mitc(tokenizer, text_list, maxlen = maxlen, intent_vocab = intent_vocab, disable=args.disable)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if model is None:
        model = init_mitc_model(args, from_scratch = True)

    all_input_ids, all_input_masks = trans_inputdata_mitc(InputData_list, mode = 'test')

    all_input_ids = torch.tensor(all_input_ids, dtype=torch.long).to(device)
    all_input_masks = torch.tensor(all_input_masks, dtype=torch.long).to(device)

    eval_data = TensorDataset(all_input_ids, all_input_masks)
    eval_sampler = SequentialSampler(eval_data)
    eval_dataloader = DataLoader(eval_data, sampler=eval_sampler,
                                 batch_size = args.predict_batch_size)

    model.eval()

    all_predict_intent_list = []
    all_predict_intent_label_list = []

    for input_ids, input_masks in tqdm(eval_dataloader, desc = 'mitc predict',disable = args.disable):

        input_ids = input_ids.to(device)
        input_masks = input_masks.to(device)
        # segment_ids = segment_ids.to(device)

        with torch.no_grad():

            batch_intent_logits = model(input_ids=input_ids, attention_mask=input_masks)[0]
            real_batch_size = batch_intent_logits.shape[0]

            for i in range(real_batch_size):
                predict_intents, predict_intent_labels = recover_intent(intent_vocab, batch_intent_logits[i])

                all_predict_intent_list.append(predict_intents)
                all_predict_intent_label_list.append(predict_intent_labels)

    return all_predict_intent_list,all_predict_intent_label_list
    # 后续还要更细节点

def eval_mitc(model, text_list, label_list, **kwargs):

    # kwargs = {"args":None, "tokenizer":None}
    # text_list: ["请问身高多少？"] -> predict_intent_list: [['身高']] -> predict_intent_label_list: [[1,0,0,0,0,0]]
    predict_intent_list, predict_intent_label_list = predict_on_batch_mitc(model, text_list, **kwargs)
    target_list = []
    for one_text, true_intent_label, predict_intent, predict_intent_label in zip(text_list, label_list, predict_intent_list,predict_intent_label_list):
        if true_intent_label != predict_intent_label:
            print("one_text:",one_text)
            print("true_intent_label:", true_intent_label)
            print("predict_intent_label:", predict_intent_label)
            print("predict_intent:",predict_intent)
            print("-"*100)
            target_list.append(0)
        else:
            target_list.append(1)
    print("acc:",sum(target_list)/len(target_list))

if __name__ == "__main__":
    pass

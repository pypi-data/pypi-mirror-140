# -*- coding = utf-8 -*-
# @time: 2022/2/28 1:22 下午
# @Author: erazhan
# @File: train.py

# ----------------------------------------------------------------------------------------------------------------------
import os
from transformers import BertTokenizer
from tqdm import tqdm,trange

import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from torch.optim import Optimizer,Adam,SGD,Adagrad

from erazhan_algorithms.TC.train import warmup_linear

from .data import recover_intent, convert_to_inputdata_mitc, trans_inputdata_mitc
from .models import init_mitc_model

def train_mitc(**kwargs):

    # required_params = ["args", "train_text", "eval_text", "train_label", "eval_label"]
    required_params = ["args", "intent_vocab", "train_text", "train_label"]

    for one_param in required_params:
        assert one_param in kwargs, "%s not in kwargs" % (one_param)

    args = kwargs["args"]
    maxlen = args.maxlen
    intent_vocab = kwargs["intent_vocab"]
    train_text = kwargs["train_text"] # ['身高多少', '体重多少']
    train_label = kwargs["train_label"] # [["身高"], ["体重"]]

    # eval_text, eval_label
    eval_text = kwargs["eval_text"] if "eval_text" in kwargs.keys() else None
    eval_label = kwargs["eval_label"] if "eval_label" in kwargs.keys() else None

    tokenizer = kwargs["tokenizer"] if "tokenizer" not in kwargs.keys() else BertTokenizer.from_pretrained(args.bert_model)

    train_InputData_list = convert_to_inputdata_mitc(tokenizer, train_text, maxlen = maxlen, intents_list = train_label, intent_vocab = intent_vocab, disable = args.disable)
    print("len(train_InputData_list):", len(train_InputData_list))
    if eval_text is not None and eval_label is not None:
        eval_InputData_list = convert_to_inputdata_mitc(tokenizer, eval_text, maxlen = maxlen, intents_list = eval_label, intent_vocab = intent_vocab, disable = args.disable)
        print("len(eval_InputData_list):", len(eval_InputData_list))
    else:
        eval_InputData_list = None
        print("eval_InputData_list is None")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = init_mitc_model(args, from_scratch = True)
    # model.to(device)

    optimizer = Adam(model.parameters(), lr=args.learning_rate)

    # all_segment_ids
    all_input_ids, all_input_masks, all_intents_labels = trans_inputdata_mitc(train_InputData_list, mode = "train")

    all_input_ids = torch.tensor(all_input_ids, dtype=torch.long).to(device)
    all_input_masks = torch.tensor(all_input_masks, dtype=torch.long).to(device)
    # all_segment_ids = torch.tensor(all_segment_ids, dtype=torch.long).to(device)
    all_intents_labels = torch.tensor(all_intents_labels, dtype = torch.float32).to(device)

    train_data = TensorDataset(all_input_ids, all_input_masks, all_intents_labels)
    train_sampler = RandomSampler(train_data)
    train_dataloader = DataLoader(train_data, sampler = train_sampler, batch_size = args.batch_size)

    model.train()

    global_step = 0
    num_train_steps = args.epochs * len(all_input_ids) / args.batch_size

    train_intent_loss = 0 # 打印平均值

    for _ in trange(int(args.epochs), desc = "mitc train epoch", disable = args.disable):

        for step, batch in enumerate(tqdm(train_dataloader, desc = "mitc train batch", disable = args.disable)):

            input_ids, input_masks, intent_labels = batch #attention_mask=input_mask
            _, loss = model(input_ids = input_ids, attention_mask = input_masks, intent_labels = intent_labels)

            train_intent_loss += loss.item()

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

            lr_this_step = args.learning_rate * warmup_linear(global_step / num_train_steps, args.warmup_proportion)
            for param_group in optimizer.param_groups:
                param_group['lr'] = lr_this_step

            optimizer.step()
            optimizer.zero_grad()
            global_step += 1

            if global_step % args.print_steps == 0:

                train_intent_loss = train_intent_loss / args.print_steps
                print("global_step:", global_step, "current intent loss:", loss.detach().cpu().numpy(), 'average intent loss:', train_intent_loss)
                train_intent_loss = 0

            if global_step % args.save_steps == 0:

                # save model every 500 steps
                model_to_save = model.module if hasattr(model, 'module') else model

                if not os.path.exists(args.output_dir):
                    os.mkdir(args.output_dir)

                output_model_file = os.path.join(args.output_dir, "pytorch_model.bin")
                torch.save(model_to_save.state_dict(), output_model_file)

    # save model
    model_to_save = model.module if hasattr(model, 'module') else model
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    output_model_file = os.path.join(args.output_dir, "pytorch_model.bin")
    torch.save(model_to_save.state_dict(), output_model_file)

    # ------------------------------------------------------------------------------------------------------------------
    if eval_InputData_list is None:
        return

    # eval
    all_input_ids, all_input_masks, all_intents_labels = trans_inputdata_mitc(eval_InputData_list, mode = "eval")

    all_input_ids = torch.tensor(all_input_ids, dtype=torch.long).to(device)
    all_input_masks = torch.tensor(all_input_masks, dtype=torch.long).to(device)
    # all_segment_ids = torch.tensor(all_segment_ids, dtype=torch.long).to(device)

    eval_data = TensorDataset(all_input_ids, all_input_masks)
    eval_sampler = SequentialSampler(eval_data)
    eval_dataloader = DataLoader(eval_data, sampler = eval_sampler, batch_size = args.predict_batch_size)
    model.eval()

    target_list = []
    all_predict_intent_list = []
    all_predict_intent_label_list = []

    for input_ids, input_masks in tqdm(eval_dataloader, desc='Evaluating'):

        input_ids = input_ids.to(device)
        input_masks = input_masks.to(device)
        # segment_ids = segment_ids.to(device)

        with torch.no_grad():

            batch_intent_logits = model(input_ids = input_ids, attention_mask = input_masks)[0]
            real_batch_size = batch_intent_logits.shape[0]

            for i in range(real_batch_size):

                predict_intents, predict_intent_labels = recover_intent(intent_vocab, batch_intent_logits[i])

                all_predict_intent_list.append(predict_intents)
                all_predict_intent_label_list.append(predict_intent_labels)

    # 后续还要更细节点
    i = 0
    for one_eval_text,true_intent_label, predict_intent_label in zip(eval_text,all_intents_labels, all_predict_intent_label_list):

        if true_intent_label == predict_intent_label:
            one_target = 1
        else:
            i += 1
            print("i",i)
            print("eval_text", one_eval_text)
            print("true_intent_label:", true_intent_label)
            print("predict_intent_label:", predict_intent_label)

            one_target = 0

        target_list.append(one_target)

    print("acc:",sum(target_list)/len(target_list))

if __name__ == "__main__":
    pass

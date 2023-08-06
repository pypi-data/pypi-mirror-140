# -*- coding = utf-8 -*-
# @time: 2022/2/28 11:30 上午
# @Author: erazhan
# @File: data.py

# ----------------------------------------------------------------------------------------------------------------------
from tqdm import tqdm

def recover_intent(intent_vocab, intent_logits):

    '''
    :param intent_vocab: 意图字典: [发烧, 身高, 体重], 注意: 是不包括非0意图的
    :param intent_logits: 维度为(intent_num, )
    :return:
    '''

    intents = []
    intent_labels = [0] * len(intent_vocab)
    intent_num = len(intent_vocab)

    for j in range(intent_num):
        if intent_logits[j] > 0:
            intent = intent_vocab[j]
            intents.append(intent)
            intent_labels[j] = 1

    return intents, intent_labels

class InputData_mitc(object):

    def __init__(self,
                 unique_id,
                 text,
                 tokens,
                 input_ids,
                 input_masks,
                 intents = None,
                 intent_labels = None
                 ):
        '''
        :param unique_id:
        :param text:
        :param tokens:
        :param input_ids:
        :param input_masks:
        :param intents:
        :param intent_labels:
        '''
        self.unique_id = unique_id
        self.text = text
        self.tokens = tokens
        self.input_ids = input_ids
        self.input_masks = input_masks
        self.intents = intents
        self.intent_labels = intent_labels

def convert_to_inputdata_mitc(tokenizer, text_list, maxlen = 512, intents_list = None, intent_vocab = None, disable = True):

    '''
    :param tokenizer:
    :param text_list:
    :param intents_list:
    :param intent_vocab:
    :param maxlen:
    :return:
    '''

    InputData_list = []
    for unique_id in tqdm(range(len(text_list)),desc = 'convert_to_inputdata_mitc', disable = disable):

        one_text = text_list[unique_id]

        tokens = ["[CLS]"]
        # segment_ids = []
        tokens.extend(tokenizer.tokenize(one_text))
        tokens.append("[SEP]")
        # segment_ids += [0] * len(tokens)

        input_ids = tokenizer.convert_tokens_to_ids(tokens)
        input_masks = [1] * len(input_ids)

        while len(input_ids) < maxlen:
            input_ids.append(0)
            input_masks.append(0)
            # segment_ids.append(0)

        tokens = tokens[:maxlen]
        input_ids = input_ids[:maxlen]
        input_masks = input_masks[:maxlen]

        if intents_list is not None and intent_vocab is not None:
            one_intents = intents_list[unique_id]
            intent_labels = [1 if e in one_intents else 0 for e in intent_vocab]
        else:
            one_intents = None
            intent_labels = None
        one_input_data = InputData_mitc(unique_id = unique_id,
                                        text = one_text,
                                        tokens = tokens,
                                        input_ids = input_ids,
                                        input_masks = input_masks,
                                        intents = one_intents,
                                        intent_labels = intent_labels,
                                        )

        InputData_list.append(one_input_data)

    return InputData_list

def trans_inputdata_mitc(InputData_list, mode = "train"):

    '''
    :param InputData_list:
    :param mode: train or eval or test, test -> 数据没有label
    :return:
    '''

    all_input_ids, all_input_masks = [], []
    # all_segment_ids = []

    if mode == "train" or mode == "eval":
        all_intent_labels = []

    for one_inputdata in InputData_list:
        all_input_ids.append(one_inputdata.input_ids)
        all_input_masks.append(one_inputdata.input_masks)
        # all_segment_ids.append(one_inputdata.segment_ids)
        if mode == "train" or mode == "eval":
            all_intent_labels.append(one_inputdata.intent_labels)

    # result = (all_input_ids, all_input_masks, all_segment_ids)
    result = (all_input_ids, all_input_masks)

    if mode == "train" or mode == "eval":
        result += (all_intent_labels,)

    return result

if __name__ == "__main__":
    pass

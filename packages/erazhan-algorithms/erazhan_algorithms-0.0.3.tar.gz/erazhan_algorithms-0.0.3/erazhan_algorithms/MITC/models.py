# -*- coding = utf-8 -*-
# @time: 2022/2/25 6:12 下午
# @Author: erazhan
# @File: models.py

# ----------------------------------------------------------------------------------------------------------------------
import os
from transformers import BertPreTrainedModel,BertModel

import torch
from torch import nn
from torch.nn import BCEWithLogitsLoss

class Bert4MITC(BertPreTrainedModel):

    '''多意图分类模型'''
    def __init__(self, config, intent_weight = None):

        super().__init__(config)

        self.bert = BertModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.num_labels = config.num_labels
        self.dropout = nn.Dropout(config.hidden_dropout_prob)

        self.intent_classifier = nn.Linear(config.hidden_size, self.num_labels)

        self.intent_weight = intent_weight if intent_weight is not None else torch.tensor([1.] * self.num_labels)

        self.intent_loss_fct = BCEWithLogitsLoss(pos_weight = self.intent_weight)

        self.init_weights()

    def forward(self,
                input_ids=None,
                attention_mask=None,
                token_type_ids=None,
                position_ids=None,
                head_mask=None,
                inputs_embeds=None,
                intent_labels=None,
                output_attentions=None,
                output_hidden_states=None,
                return_dict=None,
                ):

        outputs = self.bert(input_ids = input_ids,
                            attention_mask = attention_mask,
                            token_type_ids=token_type_ids,
                            position_ids=position_ids,
                            head_mask=head_mask,
                            inputs_embeds=inputs_embeds,  # 有版本后面是不执行的
                            output_attentions=output_attentions,
                            output_hidden_states=output_hidden_states,
                            return_dict=return_dict, )

        # sequence_output = outputs[0]
        pooled_output = outputs[1]

        pooled_output = self.dropout(pooled_output)
        intent_logits = self.intent_classifier(pooled_output)
        outputs = (intent_logits,)

        if intent_labels is not None:
            intent_loss = self.intent_loss_fct(intent_logits, intent_labels)
            outputs = outputs + (intent_loss,)

        return outputs  # tag_logits, intent_logits, (tag_loss), (intent_loss),

def generate_intent_weight():

    # 如果context为空也必须用pad,也就是全0去替代
    # tem_weight = [2.] * self.num_sleep
    # tem_weight[0] = 1.0
    # self.intent_weight = torch.tensor(tem_weight)
    #
    # # 重要，intent_weight，参考dataloader.py
    #
    # for intent, intent_id in self.intent2id.items():
    #     neg_pos = (train_size - self.intent_weight[intent_id]) / self.intent_weight[intent_id]
    #     self.intent_weight[intent_id] = np.log10(neg_pos)
    # self.intent_weight = torch.tensor(self.intent_weight)

    pass

def init_mitc_model(args, from_scratch = True):

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if from_scratch:
        model = Bert4MITC.from_pretrained(args.bert_model, num_labels = args.mitc_num_labels)
    else:
        predict_model_file = os.path.join(args.predict_dir, "pytorch_model.bin")
        model_state_dict = torch.load(predict_model_file)
        model = Bert4MITC.from_pretrained(args.bert_model, num_labels = args.mitc_num_labels, state_dict = model_state_dict)

    model.to(device)
    return model

if __name__ == "__main__":
    pass

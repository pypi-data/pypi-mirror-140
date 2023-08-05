# -*- coding = utf-8 -*-
# @time: 2022/2/24 10:54 上午
# @Author: erazhan
# @File: __init__.py

# ----------------------------------------------------------------------------------------------------------------------
from .models import Bert4TC
from .train import train_tc
from .predict import predict_on_batch_tc,eval_tc

from .utils import DEFAULT_PARAM_DICT,OTHER_PARMA_DICT, get_parser, get_params_help
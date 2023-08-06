# -*- coding = utf-8 -*-
# @time: 2022/2/24 10:54 上午
# @Author: erazhan
# @File: __init__.py

# ----------------------------------------------------------------------------------------------------------------------
from .models import Bert4TC, init_tc_model
from .train import train_tc
from .predict import predict_on_batch_tc, eval_tc

from .utils import TC_DEFAULT_PARAM_DICT, TC_OTHER_PARAM_DICT, get_tc_parser, get_tc_params_help
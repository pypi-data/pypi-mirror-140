# -*- coding = utf-8 -*-
# @time: 2022/2/28 6:08 下午
# @Author: erazhan
# @File: __init__.py

# ----------------------------------------------------------------------------------------------------------------------
from .models import Bert4MITC, init_mitc_model
from .train import train_mitc
from .predict import predict_on_batch_mitc, eval_mitc

from .utils import MITC_DEFAULT_PARAM_DICT, MITC_OTHER_PARAM_DICT, get_mitc_parser, get_mitc_params_help
# -*- coding = utf-8 -*-
# @time: 2022/2/24 10:54 上午
# @Author: erazhan
# @File: __init__.py

# ----------------------------------------------------------------------------------------------------------------------

__version__ = "0.0.2"

from . import TC, MITC, NER, QA

from .TC.utils import TC_DEFAULT_PARAM_DICT, TC_OTHER_PARAM_DICT
from .MITC.utils import MITC_DEFAULT_PARAM_DICT, MITC_OTHER_PARAM_DICT

# from erazhan_algorithms import *, 如果定义了__all__, 则导入当中的变量等, 否则导入所有变量
__all__ = ["TC", "MITC", "NER", "QA",
           "TC_DEFAULT_PARAM_DICT", "TC_OTHER_PARAM_DICT",
           "MITC_DEFAULT_PARAM_DICT", "MITC_OTHER_PARAM_DICT"]
# Copyright 2022 OctoML. All Rights Reserved.

from cmind import utils

def init(cmind):

    from .module import CModule

    return utils.init_module(CModule, cmind, __file__)

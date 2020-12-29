# Copyright (c) 2020  PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import numpy
import math
import os
import inspect


def string(param):
    return "\'{}\'".format(param)

def name_generator(nn_name, nn_name2id):
    if nn_name in nn_name2id:
        nn_name2id[nn_name] += 1
    else:
        nn_name2id[nn_name] = 0
    real_nn_name = nn_name + str(nn_name2id[nn_name])
    return real_nn_name

def remove_default_attrs(layer, diff_attrs=None):
    def get_default_args(func):
        signature = inspect.signature(func)
        return {
            k: v.default
            for k, v in signature.parameters.items()
            if v.default is not inspect.Parameter.empty
        }
    kernel = layer.kernel
    attrs = layer.attrs
    if ":" in kernel or "prim" in kernel or "module" in kernel:
        return 
    is_func = True
    if "paddle.nn" in kernel and "functional"not in kernel:
        is_func = False
    import paddle
    obj = paddle
    for i, part in enumerate(kernel.split(".")):
        if i == 0:
            continue
        obj = getattr(obj, part)
    if is_func:
        func = obj
    else:
        func = obj.__init__ 
    default_attrs = get_default_args(func)
    for default_k, default_v in default_attrs.items():
        if default_k in attrs:
            if (isinstance(attrs[default_k], list) or isinstance(attrs[default_k], tuple)) \
                    and not is_func:
                if len(set(attrs[default_k])) == 1:
                    attrs[default_k] = attrs[default_k][0]
            if default_v == attrs[default_k]:
                if diff_attrs is None:
                    attrs.pop(default_k)
                else:
                    key_name = "{}_{}".format(layer.outputs[0], default_k)
                    if key_name not in diff_attrs:
                        attrs.pop(default_k)

#! /usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.


MAJOR = 0
MINOR = 0
PATCH = 0

# Use the following formatting: (major, minor, patch, prerelease)
VERSION = (MAJOR, MINOR, PATCH)

__shortversion__ = '.'.join(map(str, VERSION[:3]))
__version__ = __shortversion__ + "post1"

__contact_names__ = 'Naren Dasan'
__contact_emails__ = 'narens@nvidia.com'
__homepage__ = 'https://github.com/NVIDIA'
__repository_url__ = 'https://github.com/NVIDIA/Torch-TensorRT'
__download_url__ = 'https://github.com/NVIDIA/Torch-TensorRT/releases'
__description__ = 'Torch-TensorRT is a package which allows users to automatically compile PyTorch and TorchScript modules to TensorRT while remaining in PyTorch'
__license__ = 'BSD'
__keywords__ = 'nvidia, deep learning, machine learning, supervised learning,'
__keywords__ += 'unsupervised learning, reinforcement learning, logging'

__faked_packages__ = [
    ("torch-tensorrt", "torch-tensorrt/README.rst", "torch-tensorrt/ERROR.txt"),
]

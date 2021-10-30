#!/bin/env python
# -*- coding: utf-8 -*-

import platform
import multiprocessing

print("platform.system: ", platform.system())
print("platform.platform: ", platform.platform())
print("platform.version: ", platform.version())
print("platform.processor: ", platform.processor())
print("multiprocessing.cpu_count: ", multiprocessing.cpu_count())
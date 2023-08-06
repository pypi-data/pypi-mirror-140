/* Copyright (c) Microsoft Corporation.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/

#pragma once

#include "dml_cache.h"

// These guids are redefined here to specialize the  uuidof<T> template that is included in WSL builds.
// the uuidof template replaces the __uuidof() built in operator on Windows.
// Implementing the uuidof<T> specializations for the com types below enables QueryInterface to perform
// interface queries.

// The guids are identical to those in the dml_cache.h MIDL_INTERFACE macros.

WINADAPTER_IID(::dml::ICacheResource, 0x21b48a18, 0x9b20, 0x4394, 0xbf, 0xa2, 0x3a, 0x03, 0x94, 0xe7, 0xbf, 0x94);
WINADAPTER_IID(::dml::ICache, 0xd0600f51, 0x3c88, 0x400a, 0x83, 0x86, 0x1f, 0x0f, 0x4a, 0x71, 0xc9, 0x51);
WINADAPTER_IID(::dml::IOperatorCache, 0x9790f7a0, 0xeb80, 0x4365, 0x8e, 0xea, 0xd5, 0xb1, 0x64, 0x15, 0x26, 0x4e);
WINADAPTER_IID(::dml::IDmlTensor, 0x3f85ef8b, 0x3eed, 0x4176, 0xb1, 0x6d, 0x1a, 0xa0, 0x40, 0x6d, 0x3e, 0x40);
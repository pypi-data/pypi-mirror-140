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

#include "dml_common.h"
#include "dml_operator.h"

#ifdef _WIN32
namespace WRL {
// Helper wrapper over Microsoft::WRL::RuntimeClass. This is already implemented
// in wrladapter.h, so it is only declared for Windows builds.
template <typename... TInterfaces>
using Base = Microsoft::WRL::RuntimeClass<
    Microsoft::WRL::RuntimeClassFlags<Microsoft::WRL::ClassicCom>,
    TInterfaces...>;
}
#endif

namespace dml {

struct DmlBackend;

struct OperatorCache : public WRL::Base<IOperatorCache>
{
  STDMETHOD(HasKey)(uint64_t key, bool* out) const override;
  STDMETHOD(CacheOperator)(uint64_t key, const DmlOperatorBase* op) override;
  STDMETHOD_(DmlOperatorBase, GetOperator)(uint64_t key) const override;

private:
  std::unordered_map<uint64_t, DmlOperatorBase> cached_operators_;
};

}
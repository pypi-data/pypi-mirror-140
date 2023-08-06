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

#include <functional>

#include "dml_common.h"
#include "dml_operator.h"

namespace dml {

class HardwareAdapter;
class DmlExecutionContext;
class DmlEventQueue;
class DmlUploadHeap;
class DmlReadbackHeap;

struct ICache;

// Holds device state that is shared across one or more DmlDevice instances.
// Instances of these state objects are owned by the DML device factory.
// Typically one of these state objects exists for each physical D3D adapter,
// but multiple TF DmlDevice instances can share this state. All objects owned
// by this state object are thread-safe.
struct DmlBackend {
 public:
  DmlBackend();
  ~DmlBackend();

  static std::unique_ptr<DmlBackend> Create(const HardwareAdapter& adapter);

  template<DML_OPERATOR_TYPE TType>
  DmlOperator<TType> CreateOperator(const DML_OP_DESC<TType>& op_desc) {
    if (!DmlOperator<TType>::IsHashable()) {
      if (DmlOperatorTraits<TType>::Name != nullptr) {
        printf("[%s] Non-cache create!\n", DmlOperatorTraits<TType>::Name);
      }
      return DmlOperator<TType>(this, op_desc);
    }
    // Check the cache
    auto key = DmlOperator<TType>::CreateKey(op_desc);
    bool has_key;
    THROW_IF_FAILED(OperatorCache()->HasKey(key, &has_key));
    if (!has_key) {
      if (DmlOperatorTraits<TType>::Name != nullptr) {
        printf("[%s] Cache create!\n", DmlOperatorTraits<TType>::Name);
      }
      auto op = DmlOperator<TType>(this, op_desc);
      // We should initialize operators before putting them in the cache so that the reference to op_desc
      // is not used later on
      op.Initialize();
      THROW_IF_FAILED(OperatorCache()->CacheOperator(key, static_cast<DmlOperatorBase*>(&op)));
    } else {
      if (DmlOperatorTraits<TType>::Name != nullptr) {
        printf("[%s] Cache hit!\n", DmlOperatorTraits<TType>::Name);
      }
    }
    auto op = OperatorCache()->GetOperator(key);
    return *static_cast<DmlOperator<TType>*>(&op);
  }

  DmlOperatorBase CreateOperator(IDMLCompiledOperator* compiled_op, uint64_t key, size_t num_inputs, size_t num_outputs) {
#ifdef DEBUG_STRINGS
    printf("[%" PRIu64 "] Cache miss!\n", key);
#endif
    auto op = DmlOperatorBase(this, compiled_op, num_inputs, num_outputs);
    // We should initialize operators before putting them in the cache so that
    // the reference to op_desc is not used later on
    op.Initialize();
    THROW_IF_FAILED(OperatorCache()->CacheOperator(key, &op));
    return op;
  }

  DmlOperatorBase GetOperator(uint64_t key) {
    return OperatorCache()->GetOperator(key);
  }

  bool HasOperator(uint64_t key) {
    bool has_operator = false;
    THROW_IF_FAILED(OperatorCache()->HasKey(key, &has_operator));
#ifdef DEBUG_STRINGS
    if (has_operator) {
      printf("[%" PRIu64 "] Cache hit!\n", key);
    } else {
      printf("[%" PRIu64 "] Cache miss!\n", key);
    }
#endif
    return has_operator;
  }

  HRESULT Allocate(const std::vector<int64_t>& sizes,
                   const std::vector<int64_t>& strides,
                   DML_TENSOR_DATA_TYPE type,
                   ID3D12Resource** out);

  Microsoft::WRL::ComPtr<ICache> Cache() {
    return cache_;
  }

  Microsoft::WRL::ComPtr<IOperatorCache> OperatorCache() {
    return operator_cache_;
  }

  std::unique_ptr<HardwareAdapter> adapter;
  Microsoft::WRL::ComPtr<ID3D12Device> d3d_device;
  Microsoft::WRL::ComPtr<ID3D12CommandQueue> command_queue;
  Microsoft::WRL::ComPtr<ID3D12SharingContract> sharing_contract;
  Microsoft::WRL::ComPtr<IDMLDevice> dml_device;
  Microsoft::WRL::ComPtr<ICache> cache_;
  Microsoft::WRL::ComPtr<IOperatorCache> operator_cache_;
  std::unique_ptr<DmlExecutionContext> execution_context;
  std::unique_ptr<DmlEventQueue> event_queue;
  std::unique_ptr<DmlUploadHeap> upload_heap;
  std::unique_ptr<DmlReadbackHeap> readback_heap;
};

}  // namespace dml
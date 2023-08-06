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
#include "dml_cache.h"

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

template<typename T>
class LRUQueue {
  // LRU queue (oldest first) and map of size to LRU queue position
  std::list<T> lru;
  std::map<T, typename std::list<T>::iterator> lru_reference;

public:
  void Remove(const T& key) {
    auto existing_entry = lru_reference.find(key);
    assert(existing_entry != std::end(lru_reference));
    lru.erase(existing_entry->second);
    lru_reference.erase(existing_entry);
  }

  void Update(const T& key) {
    // Insert entry as least likely candidate for removal
    lru.push_back(key);
    const auto& lru_entry = lru_reference.find(key);
    if (lru_entry != std::end(lru_reference)) {
      // Remove existing entry and update lru_reference
      lru.erase(lru_entry->second);
      lru_entry->second = std::prev(lru.end());
    } else {
      lru_reference[key] = std::prev(lru.end());
    }

    assert(lru_reference.size() == lru.size());
  }

  auto RemoveLeastUsed() {
    auto least_used = lru.front();
    lru.pop_front();
    lru_reference.erase(least_used);
    return least_used;
  }
};

struct LRUCache : public WRL::Base<ICache>
{
  HRESULT RuntimeClassInitialize(DmlBackend* dml_backend);

  HRESULT Allocate(
    const std::vector<int64_t>& sizes,
    DML_TENSOR_DATA_TYPE type,
    IDmlTensor** out);

  STDMETHOD(Allocate)(
    const std::vector<int64_t>& sizes,
    const std::vector<int64_t>& strides,
    DML_TENSOR_DATA_TYPE type,
    IDmlTensor** out) override;

  STDMETHOD(Add)(ID3D12Resource* resource) override;

private:
  DmlBackend* dml_backend_; // weak pointer, as the cache is owned by the backend...

  static constexpr size_t max_cached_resources_ = 512;
  std::recursive_mutex mutex_;
  std::multimap<size_t, Microsoft::WRL::ComPtr<ID3D12Resource>> cached_resources_;
  LRUQueue<size_t> lru_;
};

}
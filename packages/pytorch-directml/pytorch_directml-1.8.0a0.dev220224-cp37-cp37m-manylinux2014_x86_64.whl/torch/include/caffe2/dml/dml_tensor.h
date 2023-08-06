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

struct DmlTensorCore : public WRL::Base<IDmlTensor> {
  HRESULT RuntimeClassInitialize(
    DmlBackend* backend,
    ICacheResource* cache_resource,
    const std::vector<int64_t>& sizes,
    const std::vector<int64_t>& strides,
    DML_TENSOR_DATA_TYPE type);

  STDMETHOD(GetResource)(ID3D12Resource** out) override;
  STDMETHOD(SetSizesAndStrides)(const std::vector<int64_t>& sizes,
                                const std::vector<int64_t>& strides) override;

  STDMETHOD(SetSizesPacked)(const std::vector<int64_t>& sizes) override;

  STDMETHOD(UploadToGpu)(
    const void* src,
    size_t nbytes) override;

  STDMETHOD(DownloadFromGpu)(
    void* dest,
    bool non_blocking) override;

  STDMETHOD(Copy)(
    IDmlTensor* tensor,
    uint64_t src_offset,
    uint64_t dst_offset_in_bytes,
    uint64_t byte_count,
    bool should_sync) override;

  STDMETHOD(CloneWithSharedResources)(IDmlTensor** clone) override;
  STDMETHOD(CloneWithWeakResources)(IDmlTensor** clone) override;

  STDMETHOD(SyncFromParent)() override;
  STDMETHOD(SyncToParent)() const override;
  STDMETHOD_(size_t, Rank)() override;
  STDMETHOD_(const std::vector<int64_t>&, Sizes)() const override;
  STDMETHOD_(const std::vector<int64_t>&, Strides)() const override;
  STDMETHOD_(int64_t, NumElements)() const override;
  STDMETHOD_(size_t, ElementSizeInBytes)() const override;
  STDMETHOD_(size_t, SizeInBytes)() const override;
  STDMETHOD(BufferRegion)(ID3D12Resource** out, uint64_t* offset, uint64_t* size_in_bytes) override;

private:
  Microsoft::WRL::ComPtr<ICacheResource> cache_resource_;
  std::vector<int64_t> sizes_;
  std::vector<int64_t> strides_;
  int64_t num_elements_;
  DML_TENSOR_DATA_TYPE type_;
  size_t element_size_in_bytes_;
  DmlBackend* backend_ = nullptr;
};

size_t CalculateSizeInBytes(const std::vector<int64_t>& sizes,
                            const std::vector<int64_t>& strides,
                            DML_TENSOR_DATA_TYPE type);

}  // namespace dml

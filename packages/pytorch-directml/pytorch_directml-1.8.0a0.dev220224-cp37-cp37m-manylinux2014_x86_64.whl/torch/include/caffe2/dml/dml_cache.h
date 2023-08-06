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

#include <vector>

#include "DirectML.h"

namespace dml {

struct DmlOperatorBase;

interface DML_DECLARE_INTERFACE("3f85ef8b-3eed-4176-b16d-1aa0406d3e40") IDmlTensor : IUnknown
{
  IFACEMETHOD(GetResource)(
    ID3D12Resource** out) = 0;

  IFACEMETHOD(SetSizesAndStrides)(
    const std::vector<int64_t>& sizes,
    const std::vector<int64_t>& strides) = 0;

  IFACEMETHOD(SetSizesPacked)(
    const std::vector<int64_t>& sizes) = 0;

  IFACEMETHOD(UploadToGpu)(
    const void* src,
    size_t nbytes) = 0;

  IFACEMETHOD(DownloadFromGpu)(
    void* dest,
    bool non_blocking) = 0;

  IFACEMETHOD(Copy)(
    IDmlTensor* tensor,
    uint64_t src_offset,
    uint64_t dst_offset_in_bytes,
    uint64_t byte_count,
    bool should_sync) = 0;

  IFACEMETHOD(CloneWithSharedResources)(
    IDmlTensor** clone) = 0;

  IFACEMETHOD(CloneWithWeakResources)(
    IDmlTensor** clone) = 0;

  IFACEMETHOD(SyncFromParent)() = 0;

  IFACEMETHOD(SyncToParent)() const = 0;

  STDMETHOD_(size_t, Rank)() = 0;

  STDMETHOD_(const std::vector<int64_t>&, Sizes)() const = 0;

  STDMETHOD_(const std::vector<int64_t>&, Strides)() const = 0;

  STDMETHOD_(int64_t, NumElements)() const = 0;

  STDMETHOD_(size_t, ElementSizeInBytes)() const = 0;

  STDMETHOD_(size_t, SizeInBytes)() const = 0;

  IFACEMETHOD(BufferRegion)(
    ID3D12Resource** out,
    uint64_t* offset,
    uint64_t* size_in_bytes) = 0;
};

interface DML_DECLARE_INTERFACE("21b48a18-9b20-4394-bfa2-3a0394e7bf94") ICacheResource : IUnknown
{
  IFACEMETHOD(Get)(ID3D12Resource** out) = 0;
};


interface DML_DECLARE_INTERFACE("d0600f51-3c88-400a-8386-1f0f4a71c951") ICache : IUnknown
{
  IFACEMETHOD(Allocate)(
    const std::vector<int64_t>& sizes,
    const std::vector<int64_t>& strides,
    DML_TENSOR_DATA_TYPE type,
    IDmlTensor** out) = 0;

  IFACEMETHOD(Allocate)(
    const std::vector<int64_t>& sizes,
    DML_TENSOR_DATA_TYPE type,
    IDmlTensor** out) = 0;

  IFACEMETHOD(Add)(
    ID3D12Resource* resource) = 0;
};

interface DML_DECLARE_INTERFACE("9790f7a0-eb80-4365-8eea-d5b16415264e") IOperatorCache : IUnknown
{
  IFACEMETHOD(HasKey)(
    uint64_t key,
    bool* out) const = 0;

  IFACEMETHOD(CacheOperator)(
    uint64_t key,
    const DmlOperatorBase* op) = 0;

  STDMETHOD_(DmlOperatorBase, GetOperator)(
    uint64_t key) const = 0;
};

}
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

#include "dml_buffer_region.h"
#include "c10/core/ScalarType.h"

#include "dml_buffer_region.h"
#include <ATen/Tensor.h>
#include "aten/src/ATen/native/dml/DMLTensor.h"
#include "dml_tensor_desc.h"

namespace dml {

Microsoft::WRL::ComPtr<IDMLDevice> CreateDmlDevice(
  ID3D12Device* d3d12_device, DML_CREATE_DEVICE_FLAGS dml_flags);

DML_TENSOR_DATA_TYPE GetDmlDataTypeFromC10ScalarType(c10::ScalarType type);
DML_SCALAR_UNION CreateDmlScalarUnionFromC10Scalar(c10::ScalarType type, c10::Scalar scalar);

dml::D3D12BufferRegion ToDmlBufferRegion(const at::Tensor& tensor);

dml::DmlTensorDesc CreateDmlTensorDesc(
  const at::Tensor& tensor,
  const std::vector<int64_t>& broadcast_dimensions,
  bool map_unsafe_types = false);

dml::DmlTensorDesc CreateDmlTensorDesc(
  const at::Tensor& tensor,
  DML_TENSOR_DATA_TYPE dml_data_type,
  const std::vector<int64_t>& broadcast_dimensions,
  bool map_unsafe_types = false);

// Converts a TF TensorShape into an array of uint32_t, and validates that the
// shape is representable as uint32_t. This is useful because shapes in TF are
// logically represented as int64, whereas DML requires uint32.
template <int dim_count = 4>
dml::SmallVector<uint32_t, dim_count> NarrowTensorShape(
    const caffe2::TensorShape& shape) {
  CHECK(shape.dims_size() >= 0);  // No partial tensor shapes allowed

  dml::SmallVector<uint32_t, dim_count> narrowed_shape;
  for (int i = 0; i < shape.dims_size(); ++i) {
    int64_t dim = shape.dims(i);

    CHECK(dim >= 0 && dim <= UINT32_MAX);
    narrowed_shape.push_back(static_cast<uint32_t>(dim));
  }

  return narrowed_shape;
}

// Retrieves the index in canonical DML order (NCHW/NCDHW) of the specified
// axis. For example, the index of the 'H' dimension is 2 for 4D tensors descs,
// and 3 for 5D tensor descs.
uint32_t GetDmlDimensionIndex(DmlTensorAxis axis, uint32_t dml_dimension_count);

// Converts a TF-style TensorFormat and rank (or "dimension count") into an
// equivalent DmlTensorLayout. If rank < 4, this function defaults to dropping
// dimensions from the left. For example, a format of NHWC and rank of 2 results
// in a DML tensor layout of WC.

DmlTensorLayout GetDmlTensorLayout(TensorFormat format, uint32_t rank);
/*
// Converts a TF-style TensorFormat into the equivalent DirectMLX enum value.
dml::TensorLayout GetDmlXTensorLayout(TensorFormat format);
*/
namespace dml_util {

// Calls D3D12BufferRegion::GetBufferBinding on each of the buffers and returns
// the result.
dml::SmallVector<c10::optional<DML_BUFFER_BINDING>, 8> GetBufferBindings(
    dml::detail::span<const D3D12BufferRegion> buffers);
inline bool HrIsOutOfMemory(HRESULT hr) {
  // E_OUTOFMEMORY has a different value depending on whether _WIN32 is defined
  // when building winerror.h, so we check both potential values here
  return hr == 0x80000002 || hr == 0x8007000e;
}

/*
// Reads Int64 value from environment variable
*/
Status ReadInt64FromEnvVar(
    google::protobuf::StringPiece env_var_name,
    int64_t default_val,
    int64_t* value);

bool ValidDmlTensor(
    const at::Tensor& tensor,
    const std::vector<int64_t>& expected_dimensions);
}  // namespace dml_util

}  // namespace tensorflow
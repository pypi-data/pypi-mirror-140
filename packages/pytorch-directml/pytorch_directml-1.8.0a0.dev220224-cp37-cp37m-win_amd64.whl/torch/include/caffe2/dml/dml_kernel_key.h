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

#include <cstddef>
#ifndef _WIN32
#include <wsl/winadapter.h>
#endif
#include "DirectML.h"
#include "dml_common.h"
#include "dml_operator_traits.h"
#include "caffe2/core/blob_serialization.h"

namespace dml {

inline uint32_t DecodeFixed32(const char* ptr) {
  if (kIsLittleEndian) {
    // Load the raw bytes
    uint32_t result;
    memcpy(&result, ptr, sizeof(result)); // gcc optimizes this to a plain load
    return result;
  } else {
    return (
        (static_cast<uint32_t>(static_cast<unsigned char>(ptr[0]))) |
        (static_cast<uint32_t>(static_cast<unsigned char>(ptr[1])) << 8) |
        (static_cast<uint32_t>(static_cast<unsigned char>(ptr[2])) << 16) |
        (static_cast<uint32_t>(static_cast<unsigned char>(ptr[3])) << 24));
  }
}

inline uint64_t DecodeFixed64(const char* ptr) {
  if (kIsLittleEndian) {
    // Load the raw bytes
    uint64_t result;
    memcpy(&result, ptr, sizeof(result)); // gcc optimizes this to a plain load
    return result;
  } else {
    uint64_t lo = DecodeFixed32(ptr);
    uint64_t hi = DecodeFixed32(ptr + 4);
    return (hi << 32) | lo;
  }
}
inline uint64_t ByteAs64(char c) {
  return static_cast<uint64_t>(c) & 0xff;
}

uint64_t Hash64(const char* data, size_t n, uint64_t seed);

inline uint64_t Hash64(const char* data, size_t n) {
  return Hash64(data, n, 0xDECAFCAFFE);
}

inline uint64_t Hash64(const std::string& str) {
  return Hash64(str.data(), str.size());
}

inline uint64_t Hash64Combine(uint64_t a, uint64_t b) {
  return a ^ (b + 0x9e3779b97f4a7800ULL + (a << 10) + (a >> 4));
}

inline uint64_t TensorShapeHash(const caffe2::TensorShape& s) {
  uint64_t hash = s.dims_size();
  for (int i = 0; i < s.dims_size(); ++i) {
    hash = Hash64Combine(hash, s.dims(i));
  }
  return hash;
}

template <typename T>
struct convert_to_uint64_t {
  static uint64_t val(T in) {
    return static_cast<uint64_t>(in);
  }
};

template <>
struct convert_to_uint64_t<int> {
  static uint64_t val(int in) {
    auto in_casted = *reinterpret_cast<unsigned*>(&in);
    return static_cast<uint64_t>(in_casted);
  }
};

template <>
struct convert_to_uint64_t<bool> {
  static uint64_t val(bool in) {
    auto in_casted = *reinterpret_cast<unsigned char*>(&in);
    return static_cast<uint64_t>(in_casted);
  }
};

template <>
struct convert_to_uint64_t<float> {
  static uint64_t val(float in) {
    double in_casted = static_cast<double>(in);
    return *reinterpret_cast<uint64_t*>(&in_casted);
  }
};

template <>
struct convert_to_uint64_t<double> {
  static uint64_t val(double in) {
    return *reinterpret_cast<uint64_t*>(&in);
  }
};

// Buffer to add all key data for hashing
struct DmlKernelKeyBuffer {
  std::vector<uint64_t> data_;

  template<typename... T>
  DmlKernelKeyBuffer& AddInts(T... n) {
    data_.insert(std::end(data_), { convert_to_uint64_t<T>::val(n)... });
    return *this;
  }

  template<typename T>
  DmlKernelKeyBuffer& AddArray(const T* a, size_t n) {
    data_.reserve(data_.size() + n);
    for (size_t i = 0; i < n; ++i) {
      data_.push_back(a[i]);
    }
    return *this;
  }

  template<typename T, unsigned count>
  DmlKernelKeyBuffer& AddString(const T (&a)[count]) {
    return AddArray(a, count);
  }

  DmlKernelKeyBuffer& AddDmlTensorDesc(const DML_TENSOR_DESC* tensor_description) {
    if (!tensor_description) {
      data_.push_back(std::numeric_limits<uint64_t>::max());
      return *this;
    }
    data_.push_back(tensor_description->Type);
    if (tensor_description->Desc) {
      // Only buffer tensors are supported right now.
      assert(tensor_description->Type == DML_TENSOR_TYPE_BUFFER);
      auto description = reinterpret_cast<const DML_BUFFER_TENSOR_DESC*>(tensor_description->Desc);
      AddInts(description->DataType, description->Flags, description->DimensionCount, description->TotalTensorSizeInBytes, description->GuaranteedBaseOffsetAlignment);
      AddArray(description->Sizes, description->DimensionCount);
      AddArray(description->Strides, description->DimensionCount);
    }
    return *this;
  }

  template<typename... T>
  DmlKernelKeyBuffer& AddScaleBias(const DML_SCALE_BIAS* scale_bias) {
    if (scale_bias != nullptr) {
      AddInts(scale_bias->Scale, scale_bias->Bias);
    }
    return *this;
  }

  uint64_t Hash() {
    return Hash64(reinterpret_cast<char*>(data_.data()), data_.size() * sizeof(uint64_t));
  }

  bool operator==(const DmlKernelKeyBuffer& other) const { return data_ == other.data_; }
};

// Uniquely identifes a DML kernel instance. This is used for caching of
// kernels, since DML kernels are immutable once constructed.
template<DML_OPERATOR_TYPE TType>
struct DmlKernelKey {
  // Default implementation if none is given
  DmlKernelKey(const void*) {
    std::abort();
  }

  uint64_t Hash() const {
    std::abort();
  }

  static constexpr bool implemented = false;
};

template<DML_OPERATOR_TYPE T>
bool operator==(const DmlKernelKey<T>&, const DmlKernelKey<T>&) { abort(); }


template <DML_OPERATOR_TYPE TType>
struct DmlKernelKeyBase {
  constexpr static bool implemented = true;
  DmlKernelKeyBuffer data_;
  uint64_t hash_;

  uint64_t Hash() const {
    return hash_;
  }

  bool operator==(const DmlKernelKey<TType>& other) const {
    return data_ == other.data_;
  }
};

}  // namespace dml

#include "dml_kernel_key.inl"
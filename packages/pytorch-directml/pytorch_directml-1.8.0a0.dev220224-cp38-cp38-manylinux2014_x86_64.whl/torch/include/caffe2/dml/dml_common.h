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
#include <deque>
#include <mutex>
#include <chrono>

#ifndef _WIN32
#include "wsl/winadapter.h"
#endif

#include <d3d12.h>
#include "d3dx12.h"

#include <wrl/client.h>
#include <wrl/implements.h>

#if _WIN32
#include <dxgi1_6.h>
#else
#include <dxcore.h>
#endif

#include "proto/caffe2_pb.h"
#define DML_TARGET_VERSION_USE_LATEST 1
#include "DirectML.h"
#include "DirectMLX.h"

#include "dml_cache.h"

#ifndef _WIN32
#include "dxguids/dxguids.h"
#include "dml_guids.h"
#include "dml_torch_guids.h"
#endif

#define THROW_IF_FAILED(x) DML_CHECK_SUCCEEDED(x)
#define THROW_IF_STATUS_FAILED(status) if (!status.ok()) { throw std::system_error{status.error_code(), std::system_category()}; }

// Drop-in C++11-compatible replacements for optional, variant, and small_vector
// which are used by the external ApiHelpers.h header
#include <c10/util/SmallVector.h>
namespace dml {
template <typename T, size_t N>
using small_vector = c10::SmallVector<T, N>;
}  // namespace dml

using byte = unsigned char;

#include "dml_error_handling.h"

// This enum is deliberately not given contiguous integral values to prevent
// accidental use of these values as indices, because doing so is usually wrong.
// These axes should be thought of as being symbolic/logical, because the
// mapping between logical axis and index of the dimension depends on the tensor
// layout. For example, the location of Conv2D's 'C' dimension depends on that
// operator's data_layout attribute so it's usually wrong to assume that e.g.
// the 'C' dimension always lives at index 1. Use the `GetDmlDimensionIndex`
// helper utility to convert from this tensor axis to the corresponding index of
// the dimension in a DML_TENSOR_DESC.
enum class DmlTensorAxis : char {
  N = 'N',
  C = 'C',
  D = 'D',
  H = 'H',
  W = 'W',
};

// These are placed in a namespace for convenience so you can `using namespace`
// to save from typing DmlTensorAxis:: everywhere.
namespace DmlTensorAxes {
static constexpr auto N = DmlTensorAxis::N;
static constexpr auto C = DmlTensorAxis::C;
static constexpr auto D = DmlTensorAxis::D;
static constexpr auto H = DmlTensorAxis::H;
static constexpr auto W = DmlTensorAxis::W;
}  // namespace DmlTensorAxes

using DmlTensorLayoutBase = c10::SmallVector<DmlTensorAxis, DML_TENSOR_DIMENSION_COUNT_MAX>;

struct DmlTensorLayout : public DmlTensorLayoutBase {
  DmlTensorLayout() = default;

  // Inherit constructors from base
  using DmlTensorLayoutBase::DmlTensorLayoutBase;

  static DmlTensorLayout Nchw() {
    return {DmlTensorAxis::N, DmlTensorAxis::C, DmlTensorAxis::H,
            DmlTensorAxis::W};
  };
  static DmlTensorLayout Nhwc() {
    return {DmlTensorAxis::N, DmlTensorAxis::H, DmlTensorAxis::W,
            DmlTensorAxis::C};
  };
};

// Some operators only handle 4 dimensions.
static constexpr uint32_t kNchwDimensionCount = 4;

static constexpr uint32_t kNchwSpatialDimensionCount = 2;
static constexpr uint32_t kNcdhwDimensionCount = 5;
static constexpr uint32_t kNcdhwSpatialDimensionCount = 3;

// The batch and channel dimensions of NCW, NCHW, NCDHW....
static constexpr uint32_t kNonspatialDimensionCount = 2;

namespace WRL {
#ifdef DML_BUILD_WINDOWS
// Helper wrapper over Microsoft::WRL::RuntimeClass. This is already implemented
// in wrladapter.h, so it is only declared for Windows builds.
template <typename... TInterfaces>
using Base = Microsoft::WRL::RuntimeClass<
    Microsoft::WRL::RuntimeClassFlags<Microsoft::WRL::ClassicCom>,
    TInterfaces...>;
#endif
using namespace Microsoft::WRL;
}  // namespace WRL

namespace dml {
    // TODO: Temporarily have this enum here to resolve TensorFormat

// Tensor format for input/output activations used in convolution operations.
// The mnemonics specify the meaning of each tensor dimension sorted from
// largest to smallest memory stride.
// N = Batch, H = Image Height, W = Image Width, C = Number of Channels.
// TODO(pauldonnelly): It would probably be better to switch to a registration
// process for tensor formats, so specialized formats could be defined more
// locally to where they are used.
enum TensorFormat {
  // FORMAT_NHWC is the default format in TensorFlow.
  FORMAT_NHWC = 0,

  // FORMAT_NCHW often improves performance on GPUs.
  FORMAT_NCHW = 1,

  // NCHW_VECT_C is the most performant tensor format for cudnn6's quantized
  // int8 convolution and fused convolution. It is laid out in the same order
  // as NCHW, except that the size of the Channels dimension is divided by 4,
  // and a new dimension of size 4 is appended, which packs 4 adjacent channel
  // activations for the same pixel into an int32. Thus an NCHW format tensor
  // with dimensions [N, C, H, W] would have dimensions [N, C/4, H, W, 4] in
  // NCHW_VECT_C format.
  // A pre-condition of this format is that C must be a multiple of 4.
  FORMAT_NCHW_VECT_C = 2,

  // Similar to NHWC, but the size of the W dimension is divided by 4, and a
  // new dimension of size 4 is appended, which packs 4 adjacent activations
  // in the width dimension.
  FORMAT_NHWC_VECT_W = 3,

  // Note: although the current code in this file assumes VECT_C and VECT_W
  // enums imply int8x4 vectors, this should not be relied upon.
  // In the future we may change the meaning of these enums to include vectors
  // of other types such as int16x2, with op implementations automatically
  // determining which format is implied based on the datatype.

  // FORMAT_HWNC is for TPUs.
  FORMAT_HWNC = 4,

  // FORMAT_HWCN is for TPUs.
  FORMAT_HWCN = 5,
};
} // namespace dml

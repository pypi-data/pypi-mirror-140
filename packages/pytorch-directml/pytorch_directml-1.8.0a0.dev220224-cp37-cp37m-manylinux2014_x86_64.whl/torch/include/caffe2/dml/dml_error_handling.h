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

#include "c10/util/Logging.h"

#include "google/protobuf/stubs/status.h"
#include "google/protobuf/stubs/statusor.h"
#include "google/protobuf/stubs/logging.h"

using Status = google::protobuf::util::Status;
template <typename T>
using StatusOr = google::protobuf::util::StatusOr<T>;

// CHECK dies with a fatal error if condition is not true.  It is *not*
// controlled by NDEBUG, so the check will be executed regardless of
// compilation mode.  Therefore, it is safe to do things like:
//    CHECK(fp->Write(x) == 4)

#define DML_CHECK_SUCCEEDED(hr)             \
  do {                                      \
    GOOGLE_CHECK_EQ(SUCCEEDED((hr)), true); \
  } while (0)
// CHECK_EQ(SUCCEEDED((hr)), true);


// For propagating errors when calling a function.
#define TF_RETURN_IF_ERROR(...)                         \
  do {                                                  \
    const Status _status = (__VA_ARGS__);               \
    if (TF_PREDICT_FALSE(!_status.ok()))                \
      return _status;                                   \
  } while (0)


#ifdef __has_builtin
#define TF_HAS_BUILTIN(x) __has_builtin(x)
#else
#define TF_HAS_BUILTIN(x) 0
#endif

// Compilers can be told that a certain branch is not likely to be taken
// (for instance, a CHECK failure), and use that information in static
// analysis. Giving it this information can help it optimize for the
// common case in the absence of better information (ie.
// -fprofile-arcs).
//
// We need to disable this for GPU builds, though, since nvcc8 and older
// don't recognize `__builtin_expect` as a builtin, and fail compilation.
#if (!defined(__NVCC__)) && \
    (TF_HAS_BUILTIN(__builtin_expect) || (defined(__GNUC__) && __GNUC__ >= 3))
#define TF_PREDICT_FALSE(x) (__builtin_expect(x, 0))
#define TF_PREDICT_TRUE(x) (__builtin_expect(!!(x), 1))
#else
#define TF_PREDICT_FALSE(x) (x)
#define TF_PREDICT_TRUE(x) (x)
#endif
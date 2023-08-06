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

#include <unordered_set>

namespace dml {

enum class DmlEnvironmentVariable {
  kDmlVisibleDevices,
};

const char* DmlEnvironmentVariableNames[] = {
  "DML_VISIBLE_DEVICES"
};


template <typename T> struct StringToT; 
template <> struct StringToT<size_t> {
  static size_t Convert(const std::string& str) {
    return static_cast<size_t>(stoi(str));
  }
};

template <typename T>
struct DmlEnvironmentVariableReaderBase {
  template <template<typename...> typename C>
  static C<T> GetDelimited(DmlEnvironmentVariable environment_variable, char delim, bool skip_invalid) {
    auto out = C<T>();
    auto variable_name = DmlEnvironmentVariableNames[static_cast<size_t>(environment_variable)]; 
    if (const char* variable_value = getenv(variable_name)) {
      auto variable_value_length = strlen(variable_value);
      if (variable_value_length > 0) {
        auto start = variable_value;
        auto end = variable_value + variable_value_length;
        auto next = std::find(start, end, delim);
        while (next != end) {
          auto value = std::string(start, next);
          try {
            out.emplace(StringToT<T>::Convert(value));
          } catch (...) {
            if (!skip_invalid) {
              throw;
            }
          }
          start = next + 1;
          next = std::find(start, end, delim);
        }
      }
    }
    return out;
  }
};

template <DmlEnvironmentVariable TVariable>
struct DmlEnvironmentVariableReader;

template <>
struct DmlEnvironmentVariableReader<DmlEnvironmentVariable::kDmlVisibleDevices> {
  template <template<typename...> typename C = std::unordered_set>
  static C<size_t> GetDelimited(bool skip_invalid)
  {
    return DmlEnvironmentVariableReaderBase<size_t>::GetDelimited<C>(DmlEnvironmentVariable::kDmlVisibleDevices, ',', skip_invalid);
  }
};

}  // namespace dml
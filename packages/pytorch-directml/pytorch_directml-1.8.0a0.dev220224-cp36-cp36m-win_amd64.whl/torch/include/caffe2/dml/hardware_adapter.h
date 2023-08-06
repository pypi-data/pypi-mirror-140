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

namespace dml {

class HardwareAdapter;

enum class VendorID {
  kAmd = 0x1002,
  kNvidia = 0x10DE,
  kMicrosoft = 0x1414,
  kQualcomm = 0x5143,
  kIntel = 0x8086,
};

struct DriverVersion {
  union {
    struct {
      uint16_t d;
      uint16_t c;
      uint16_t b;
      uint16_t a;
    } parts;
    uint64_t value;
  };

  DriverVersion() = default;

  explicit DriverVersion(uint64_t value) : value(value) {}

  DriverVersion(uint16_t a, uint16_t b, uint16_t c, uint16_t d) {
    parts.a = a;
    parts.b = b;
    parts.c = c;
    parts.d = d;
  }
};

inline bool operator==(DriverVersion lhs, DriverVersion rhs) {
  return lhs.value == rhs.value;
}
inline bool operator!=(DriverVersion lhs, DriverVersion rhs) {
  return lhs.value != rhs.value;
}
inline bool operator<=(DriverVersion lhs, DriverVersion rhs) {
  return lhs.value <= rhs.value;
}
inline bool operator>=(DriverVersion lhs, DriverVersion rhs) {
  return lhs.value >= rhs.value;
}
inline bool operator<(DriverVersion lhs, DriverVersion rhs) {
  return lhs.value < rhs.value;
}
inline bool operator>(DriverVersion lhs, DriverVersion rhs) {
  return lhs.value > rhs.value;
}

class HardwareAdapterInfo
{
  friend class HardwareAdapter;

 private:
  HardwareAdapterInfo() = default;

 public:
  DriverVersion DriverVersion() const;
  VendorID VendorId() const;
  uint32_t DeviceId() const;
  const std::string& Name() const;
  bool IsComputeOnly() const;
  uint64_t GetTotalDedicatedMemory() const;

 private:
  dml::DriverVersion driver_version_;
  dml::VendorID vendor_id_;
  uint32_t device_id_;
  std::string description_;
  bool is_compute_only_;
  uint64_t dedicated_memory_in_bytes_;
};

class HardwareAdapter 
{
 public:
  HardwareAdapter(const HardwareAdapter& adapter) = default;

  static std::vector<HardwareAdapter> Enumerate(
    const std::unordered_set<size_t>& visible_device_list, bool skip_invalid);

  // OS neurtral APIs. See implementation in HardwareAdapter.cc
  IUnknown* Get() const;
  std::shared_ptr<HardwareAdapterInfo> Info() const;
  bool SupportsAllDataTypes();

  // OS specific APIs. See implementation in windows/hardware_adapter_win.cc or wsl/hardware_adapter_wsl.cc
  uint64_t QueryAvailableDedicatedMemory() const;
  static std::vector<HardwareAdapter> Enumerate();
  static HardwareAdapter Create(LUID adapter_luid);
  static HardwareAdapter Create(IUnknown* adapter);

 private:
  HardwareAdapter() = default;

 private:
  Microsoft::WRL::ComPtr<IUnknown> adapter_ = nullptr;
  std::shared_ptr<HardwareAdapterInfo> info_ = nullptr;
};

using HardwareAdapterList = std::vector<HardwareAdapter>;

}  // namespace dml
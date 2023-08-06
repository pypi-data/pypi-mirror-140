#pragma once

#include <c10/core/TensorOptions.h>
#include <c10/core/Device.h>

// cuda_lazy_init() is always compiled, even for CPU-only builds.
// Thus, it does not live in the cuda/ folder.

namespace torch {
namespace utils {

void dml_lazy_init();
void dml_lazy_init(c10::DispatchKey dispatch_key);
void dml_lazy_init(const c10::Device device);
void dml_lazy_init(const at::TensorOptions& options);

}
}

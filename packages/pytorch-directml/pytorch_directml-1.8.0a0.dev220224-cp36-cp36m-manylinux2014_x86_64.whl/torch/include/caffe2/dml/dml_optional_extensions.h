#include <c10/util/Optional.h>

namespace dml
{
    template <typename T>
    using Optional = c10::optional<T>;
    constexpr c10::nullopt_t NullOpt = c10::nullopt;
}
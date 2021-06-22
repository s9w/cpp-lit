# C++ Library Include Times (CPP-LIT :fire:)
This repo answers the question: how much time is added to my compile time by a single inclusion of `<header>`? Featuring *all* C++ Standard Library headers, their C++20 [module versions](https://docs.microsoft.com/en-us/cpp/cpp/modules-cpp?view=vs-2019) as comparison, `windows.h` and a couple of other third party libraries. All times are for Visual Studio 2019 16.11.0 Preview 2.0. The red entries are new C++20 headers.

![results](lit.png)

## Interpretation & notes
The numbers are measured with care, but are easy to misinterpret. Note:

- This analysis was done by including the headers into `.cpp` files. That accurately measures inclusion time, but isn't necessarily a good metric for actual *compile times*. The measurement code doesn't *do* anything with those headers. The cost of heavy template usage for example might outweigh the cost of merely including a header.

- Headers can themselves include other headers. Since all headers are at most included once (`#pragma once`) per TU, the include time of any header depends on whether any of its sub-includes have been included before. The worst case is when no other headers were included before and the best case is when all sub-headers were already included. This analysis compares zero includes vs the include of any header - so it's the worst case. This is a somewhat realistic scenario for sparse use of the standard library. Not so much when there's already a big list of includes.

- When compiling a project with multiple translation units and with [`/MP` enabled](https://docs.microsoft.com/en-us/cpp/build/reference/mp-build-with-multiple-processes), MSVC compiles all TUs in parallel. In such cases, the include times above can be misleading. Example: the time for one `<regex>` is around half a second for one thread. During that half second, the other n-1 cores can compile other translation units, reducing the actual added include time to about *t*/*n*, with *t* being the include time as listed and *n* being the number of threads compiling.

- Especially with some of the third party libraries, the situation is more complex than can be summarized with a single value. Some libraries offer different versions with better compile performance, like [spdlog](https://github.com/gabime/spdlog), which explicitly recommends against the use of the single-header version which was used here. Others like [glm](https://github.com/g-truc/glm) are modularized: I used the heavy `glm.hpp` - using a smaller subset *will* be faster. This was done for simplicity and not to portrait any of those libraries in a bad light.

- There is no use of PCH, header units or any form of caching. The tests were done on a fast SSD and a Ryzen 3800X. All tests were done with a warmup phase and on an otherwise idle system, so real-world numbers will probably come down higher than this.

- The standard library in module form was so fast to include that it can barely be measured or seen, at least in comparison with the rest. That's not a mistake.

## Libraries
`windows.h [MAL]` refers to the common
```
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
```

- [tracy](https://github.com/wolfpld/tracy) v0.7.8, obviously with the `TRACY_ENABLE` define.
- [spdlog](https://github.com/gabime/spdlog) v1.8.5 using header-only version with only `spdlog.h` included. Note that the readme recommends to use the static lib version instead for faster compile times.
- [fmt](https://github.com/fmtlib/fmt) v7.1.3 including only `fmt/core.h`.
- [JSON for Modern C++](https://github.com/nlohmann/json) v3.9.1. Note that this is split into the main header (nl_json - `json.hpp`) and the forward include header (nl_json_fwd - `json_fwd.hpp`). The latter is what you would include more often.
- [ned14/outcome](https://github.com/ned14/outcome) v2.1.3.
- [glm](https://github.com/g-truc/glm) v0.9.9.8. glm is very modular, this measures the include of `glm.hpp` - which might be on the larger side of what you would typically include.

## Methodology
All reported times are based on release builds. The complete compile command without includes is:

```
cl.exe /O2 /GL /Oi /MD /D NDEBUG /std:c++latest /experimental:module /EHsc /nologo <sources> /link /MACHINE:X64 /LTCG:incremental
```

To measure the cost of an include, the difference was taken between a build with that include and one without. Since the include times for most headers are small, measurement errors are a big concern. Subtracting two equally large numbers results in huge errors even if their relative errors are small. Especially for the best case standard header scenarios that was tricky. All measurements were taken after a warm-up phase and with lots of data points.

The plotted errors are the standard deviations of those numbers. The results computed as a difference, so A-B. Error propagation tells us the resulting standard deviation is:

σ = sqrt(σ_A^2 + σ_B^2)

The sources being compiled consist of 10 identical translation units with the resulting time being divided by 10 to get the individual cost.  That was done to reduce statistical noise that was caused by the many small file system operations.


TODO: add vulkan.hpp
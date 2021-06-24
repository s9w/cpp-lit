# C++ Library Include Times (CPP-LIT :fire:)
This repo answers the question: how much time is added to my compile time by a single inclusion of `<header>`? Featuring *all* C++ Standard Library headers, their C++20 [module versions](https://docs.microsoft.com/en-us/cpp/cpp/modules-cpp?view=vs-2019), `windows.h` and a couple of other third party libraries. All times are for Visual Studio 2019 16.11.0 Preview 2.0. The red entries are new C++20 headers.

![results](https://user-images.githubusercontent.com/6044318/123312578-d5f5dc80-d528-11eb-841f-a03f76a5ff4d.png)

## Interpretation & notes
The numbers are measured with care, but are easy to misinterpret. Note:

- This analysis was done by including the headers into `.cpp` files. That accurately measures inclusion time, but is only a lower limit for actual **compile times**. The measurement code doesn't *do* anything with those headers. The cost of heavy template usage for example might outweigh the cost of merely including a header.

- Headers can themselves include other headers. Since each header is at most included once (`#pragma once`) per TU, the include time of any header depends on whether any of its sub-includes have been included before. The worst case is when no other headers were included before and the best case is when all sub-headers were already included. This analysis compares zero includes vs the include of any header - so it's the **worst case**. This is a somewhat realistic scenario for sparse use of the standard library. Not so much when there's already a lenghty include list.

- When compiling a project with **multiple translation units** and with [`/MP` enabled](https://docs.microsoft.com/en-us/cpp/build/reference/mp-build-with-multiple-processes), MSVC compiles TUs in parallel. In such cases, the include times above can be misleading. Example: the time for one `<regex>` is around half a second for one thread. During that half second, the other n-1 cores can compile other translation units, reducing the actual added include time to about *t*/*n*, with *t* being the include time as listed and *n* being the number of threads compiling.

- Especially with some of the **third party libraries**, the situation is more complex than can be summarized with a single value. Some libraries offer different versions with better compile performance, like [spdlog](https://github.com/gabime/spdlog), which explicitly recommends against the use of the single-header version which was used here. Others like [GLM](https://github.com/g-truc/glm) are modularized: I used the heavy `glm.hpp` - using a smaller subset *will* be faster. This was done for simplicity and not to portray any of those libraries in a bad light.

- There is no use of PCH, header units or any form of caching. The tests were done on a fast SSD and a Ryzen 3800X. All tests were done with a warmup phase and on an otherwise idle system, so real-world numbers will probably come down higher than this.

- The standard library in **module** form was so fast to include that it can barely be measured or seen, at least in comparison with the rest. That's not a mistake.

## Libraries
`windows.h [LAM]` refers to the common
```
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
```

- [Tracy](https://github.com/wolfpld/tracy) v0.7.8, obviously with the `TRACY_ENABLE` define.
- [spdlog](https://github.com/gabime/spdlog) v1.8.5 using header-only version with only `spdlog.h` included. Note that the readme recommends to use the static lib version instead for faster compile times.
- [{fmt}](https://github.com/fmtlib/fmt) v7.1.3 including only `fmt/core.h`.
- [JSON for Modern C++](https://github.com/nlohmann/json) v3.9.1. Note that this is split into the main header (nl_json - `json.hpp`) and the forward include header (nl_json_fwd - `json_fwd.hpp`). The latter is what you would include more often.
- [GLM](https://github.com/g-truc/glm) v0.9.9.8. GLM is modular, this repo measures the include of `glm.hpp` - which might be more than what would typically include.
- [vulkan.h](https://www.lunarg.com/vulkan-sdk/) and `vulkan.hpp` (not to be confused!) from Vulkan SDK v1.2.162.1.
- All boost libraries are v1.76.0. Note that [Boost.JSON](https://www.boost.org/doc/libs/1_76_0/libs/json/doc/html/index.html) is being measured in its header-only mode.
- [stb](https://github.com/nothings/stb) headers are from 2020-09-14.
- [EnTT](https://github.com/skypjack/entt) v3.5.0.

## Methodology
All reported times are based on release builds. The complete compile command without includes is:

```
cl.exe /O2 /GL /Oi /MD /D NDEBUG /std:c++latest /experimental:module /EHsc /nologo <sources> /link /MACHINE:X64 /LTCG:incremental
```

To measure the cost of an include, the difference was taken between a build with that include and one without. All measurements were taken after a warm-up phase and with lots of data points. The plotted errors are the standard deviations of those numbers. The results are computed as a difference. Error propagation tells us the resulting standard deviation is:

σ = sqrt(σ_A² + σ_B²)

The sources being compiled consist of 10 identical translation units with the resulting time being divided by 10 to get the individual cost.

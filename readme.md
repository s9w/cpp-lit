# C++ library include times (CPP-LIT :fire:)
This repo answers the question: how much time is added to my compile time by a single inclusion of header X? Featuring *all* C++ Standard Library headers, C++20 [Standard Library modules](https://docs.microsoft.com/en-us/cpp/cpp/modules-cpp?view=vs-2019) as comparison, some boost headers and `windows.h`.

Only Visual Studio (the latest as of writing: 16.8.0 Preview 2) is used as a platform. `windows_mal` refers to the ubiquitous
```
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
```
I only included a couple of boost libraries since I'm not very familiar with them, and what to include is not always trivial. Note that the boost figure is on a different axis since the include times are so much higher than the rest that I didn't want to combine them.

Note that these C++20 headers aren't shipped yet but will be added as soon as they do: `barrier`, `bit`, `coroutine`, `format`, `latch`, `numbers`, `semaphore`, `source_location`, `span`, `stop_token`, `syncstream`.

![results](http://s9w.io/cpp-lit/figure.png)
![results](http://s9w.io/cpp-lit/boost.png)

My personal conclusion: Modules are fast! And string is unfortunately as expensive as it is ubiquitous.

The measurements are done on a basically empty single file project that includes one of the headers above at a time and is compiled with `CL.exe`. The baseline (or "null") measurement contains no includes. The times reported below are the difference between those two. Both Release and Debug configurations times are taken multiple times and averaged to avoid outliers. The bar width is equal to the standard deviation.

If you want to run the measurements yourself, you have to run
```
.\run_numbers.ps1 # this takes about 5 minutes on my machine, adjust paths
.\parse_numbers.ps1
```
And then plot however you like. The plotting script I used is under `plotting`.

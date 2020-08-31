# C++ Standard Library include times (CPPSLIT)
Investigation of the time that is added by including one of the ~85 C++ standard library headers.

This project only looks at MSVC (the latest as of writing: 16.8.0 Preview 2). All available standard libary headers were taken from [cppreference.com](https://en.cppreference.com/w/cpp/header) (I didn't know there were so many!).

<details>
<summary>With C++20 support enabled, there are 85 available on that platform:</summary>
- algorithm
- any
- array
- atomic
- bitset
- cassert
- cctype
- cerrno
- cfenv
- cfloat
- charconv
- chrono
- cinttypes
- climits
- clocale
- cmath
- compare
- complex
- concepts
- condition_variable
- csetjmp
- csignal
- cstdarg
- cstddef
- cstdint
- cstdio
- cstdlib
- cstring
- ctime
- cuchar
- cwchar
- cwctype
- deque
- exception
- execution
- filesystem
- forward_list
- fstream
- functional
- future
- initializer_list
- iomanip
- ios
- iosfwd
- iostream
- istream
- iterator
- limits
- list
- locale
- map
- memory_resource
- memory
- mutex
- new
- numeric
- optional
- ostream
- queue
- random
- ranges
- ratio
- regex
- scoped_allocator
- set
- shared_mutex
- sstream
- stack
- stdexcept
- streambuf
- string_view
- string
- system_error
- thread
- tuple
- type_traits
- typeindex
- typeinfo
- unordered_map
- unordered_set
- utility
- valarray
- variant
- vector
- version
</details>

These C++20 headers aren't shipped yet: `barrier`, `bit`, `coroutine`, `format`, `latch`, `numbers`, `semaphore`, `source_location`, `span`, `stop_token`, `syncstream`.

The measurements are done on a basically empty single file project that includes one of the headers above at a time and is compiled with MSBuild. Both Release and Debug configurations times are taken 10 times and averaged to avoid outliers. The running of the builds and time-taking is done with a PowerShell script. A little interpreter C++ program was written to parse the timing files and calculate mean and standard deviation. The final visualization was done with a Matplotlib script.

If you want to run the measurements yourself, you have to run
```
.\run_numbers.ps1 # this takes about 25 minutes in my machine
.\parse_numbers.ps1
```
And then plot however you like. The notebook is under `plotting`.

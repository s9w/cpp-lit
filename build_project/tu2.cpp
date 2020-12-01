#if defined(all_std)
#ifndef no_algorithm
#include <algorithm>
#endif
#ifndef no_any
#include <any>
#endif
#ifndef no_array
#include <array>
#endif
#ifndef no_atomic
#include <atomic>
#endif
#ifndef no_bitset
#include <bitset>
#endif
#ifndef no_cassert
#include <cassert>
#endif
#ifndef no_cctype
#include <cctype>
#endif
#ifndef no_cerrno
#include <cerrno>
#endif
#ifndef no_cfenv
#include <cfenv>
#endif
#ifndef no_cfloat
#include <cfloat>
#endif
#ifndef no_charconv
#include <charconv>
#endif
#ifndef no_chrono
#include <chrono>
#endif
#ifndef no_cinttypes
#include <cinttypes>
#endif
#ifndef no_climits
#include <climits>
#endif
#ifndef no_clocale
#include <clocale>
#endif
#ifndef no_cmath
#include <cmath>
#endif
#ifndef no_compare
#include <compare>
#endif
#ifndef no_complex
#include <complex>
#endif
#ifndef no_concepts
#include <concepts>
#endif
#ifndef no_condition_variable
#include <condition_variable>
#endif
#ifndef no_csetjmp
#include <csetjmp>
#endif
#ifndef no_csignal
#include <csignal>
#endif
#ifndef no_cstdarg
#include <cstdarg>
#endif
#ifndef no_cstddef
#include <cstddef>
#endif
#ifndef no_cstdint
#include <cstdint>
#endif
#ifndef no_cstdio
#include <cstdio>
#endif
#ifndef no_cstdlib
#include <cstdlib>
#endif
#ifndef no_cstring
#include <cstring>
#endif
#ifndef no_ctime
#include <ctime>
#endif
#ifndef no_cuchar
#include <cuchar>
#endif
#ifndef no_cwchar
#include <cwchar>
#endif
#ifndef no_cwctype
#include <cwctype>
#endif
#ifndef no_deque
#include <deque>
#endif
#ifndef no_exception
#include <exception>
#endif
#ifndef no_execution
#include <execution>
#endif
#ifndef no_filesystem
#include <filesystem>
#endif
#ifndef no_forward_list
#include <forward_list>
#endif
#ifndef no_fstream
#include <fstream>
#endif
#ifndef no_functional
#include <functional>
#endif
#ifndef no_future
#include <future>
#endif
#ifndef no_initializer_list
#include <initializer_list>
#endif
#ifndef no_iomanip
#include <iomanip>
#endif
#ifndef no_ios
#include <ios>
#endif
#ifndef no_iosfwd
#include <iosfwd>
#endif
#ifndef no_iostream
#include <iostream>
#endif
#ifndef no_istream
#include <istream>
#endif
#ifndef no_iterator
#include <iterator>
#endif
#ifndef no_limits
#include <limits>
#endif
#ifndef no_list
#include <list>
#endif
#ifndef no_locale
#include <locale>
#endif
#ifndef no_map
#include <map>
#endif
#ifndef no_memory_resource
#include <memory_resource>
#endif
#ifndef no_memory
#include <memory>
#endif
#ifndef no_mutex
#include <mutex>
#endif
#ifndef no_new
#include <new>
#endif
#ifndef no_numeric
#include <numeric>
#endif
#ifndef no_optional
#include <optional>
#endif
#ifndef no_ostream
#include <ostream>
#endif
#ifndef no_queue
#include <queue>
#endif
#ifndef no_random
#include <random>
#endif
#ifndef no_ranges
#include <ranges>
#endif
#ifndef no_ratio
#include <ratio>
#endif
#ifndef no_regex
#include <regex>
#endif
#ifndef no_scoped_allocator
#include <scoped_allocator>
#endif
#ifndef no_set
#include <set>
#endif
#ifndef no_shared_mutex
#include <shared_mutex>
#endif
#ifndef no_sstream
#include <sstream>
#endif
#ifndef no_stack
#include <stack>
#endif
#ifndef no_stdexcept
#include <stdexcept>
#endif
#ifndef no_streambuf
#include <streambuf>
#endif
#ifndef no_string_view
#include <string_view>
#endif
#ifndef no_string
#include <string>
#endif
#ifndef no_system_error
#include <system_error>
#endif
#ifndef no_thread
#include <thread>
#endif
#ifndef no_tuple
#include <tuple>
#endif
#ifndef no_type_traits
#include <type_traits>
#endif
#ifndef no_typeindex
#include <typeindex>
#endif
#ifndef no_typeinfo
#include <typeinfo>
#endif
#ifndef no_unordered_map
#include <unordered_map>
#endif
#ifndef no_unordered_set
#include <unordered_set>
#endif
#ifndef no_utility
#include <utility>
#endif
#ifndef no_valarray
#include <valarray>
#endif
#ifndef no_variant
#include <variant>
#endif
#ifndef no_vector
#include <vector>
#endif
#ifndef no_version
#include <version>
#endif

#if _MSC_VER >= 1928
#ifndef no_bit
#include <bit>
#endif
#ifndef no_coroutine
#include <coroutine>
#endif
#ifndef no_numbers
#include <numbers>
#endif
#ifndef no_span
#include <span>
#endif
#endif // _MSC_VER

#endif // all_std

#ifdef i_concepts
#include <concepts>
#endif

#ifdef i_cstdlib
#include <cstdlib>
#endif

#ifdef i_csignal
#include <csignal>
#endif

#ifdef i_csetjmp
#include <csetjmp>
#endif

#ifdef i_cstdarg
#include <cstdarg>
#endif

#ifdef i_typeinfo
#include <typeinfo>
#endif

#ifdef i_typeindex
#include <typeindex>
#endif

#ifdef i_type_traits
#include <type_traits>
#endif

#ifdef i_bitset
#include <bitset>
#endif

#ifdef i_functional
#include <functional>
#endif

#ifdef i_utility
#include <utility>
#endif

#ifdef i_ctime
#include <ctime>
#endif

#ifdef i_chrono
#include <chrono>
#endif

#ifdef i_cstddef
#include <cstddef>
#endif

#ifdef i_initializer_list
#include <initializer_list>
#endif

#ifdef i_tuple
#include <tuple>
#endif

#ifdef i_any
#include <any>
#endif

#ifdef i_optional
#include <optional>
#endif

#ifdef i_variant
#include <variant>
#endif

#ifdef i_compare
#include <compare>
#endif

#ifdef i_version
#include <version>
#endif

#ifdef i_new
#include <new>
#endif

#ifdef i_memory
#include <memory>
#endif

#ifdef i_scoped_allocator
#include <scoped_allocator>
#endif

#ifdef i_memory_resource
#include <memory_resource>
#endif

#ifdef i_climits
#include <climits>
#endif

#ifdef i_cfloat
#include <cfloat>
#endif

#ifdef i_cstdint
#include <cstdint>
#endif

#ifdef i_cinttypes
#include <cinttypes>
#endif

#ifdef i_limits
#include <limits>
#endif

#ifdef i_exception
#include <exception>
#endif

#ifdef i_stdexcept
#include <stdexcept>
#endif

#ifdef i_cassert
#include <cassert>
#endif

#ifdef i_system_error
#include <system_error>
#endif

#ifdef i_cerrno
#include <cerrno>
#endif

#ifdef i_cctype
#include <cctype>
#endif

#ifdef i_cwctype
#include <cwctype>
#endif

#ifdef i_cstring
#include <cstring>
#endif

#ifdef i_cwchar
#include <cwchar>
#endif

#ifdef i_cuchar
#include <cuchar>
#endif

#ifdef i_string
#include <string>
#endif

#ifdef i_string_view
#include <string_view>
#endif

#ifdef i_charconv
#include <charconv>
#endif

#ifdef i_array
#include <array>
#endif

#ifdef i_vector
#include <vector>
#endif

#ifdef i_deque
#include <deque>
#endif

#ifdef i_list
#include <list>
#endif

#ifdef i_forward_list
#include <forward_list>
#endif

#ifdef i_set
#include <set>
#endif

#ifdef i_map
#include <map>
#endif

#ifdef i_unordered_set
#include <unordered_set>
#endif

#ifdef i_unordered_map
#include <unordered_map>
#endif

#ifdef i_stack
#include <stack>
#endif

#ifdef i_queue
#include <queue>
#endif

#ifdef i_iterator
#include <iterator>
#endif

#ifdef i_algorithm
#include <algorithm>
#endif

#ifdef i_execution
#include <execution>
#endif

#ifdef i_cmath
#include <cmath>
#endif

#ifdef i_complex
#include <complex>
#endif

#ifdef i_valarray
#include <valarray>
#endif

#ifdef i_random
#include <random>
#endif

#ifdef i_numeric
#include <numeric>
#endif

#ifdef i_ratio
#include <ratio>
#endif

#ifdef i_cfenv
#include <cfenv>
#endif

#ifdef i_locale
#include <locale>
#endif

#ifdef i_clocale
#include <clocale>
#endif

#ifdef i_iosfwd
#include <iosfwd>
#endif

#ifdef i_ios
#include <ios>
#endif

#ifdef i_istream
#include <istream>
#endif

#ifdef i_ostream
#include <ostream>
#endif

#ifdef i_iostream
#include <iostream>
#endif

#ifdef i_fstream
#include <fstream>
#endif

#ifdef i_sstream
#include <sstream>
#endif

#ifdef i_iomanip
#include <iomanip>
#endif

#ifdef i_streambuf
#include <streambuf>
#endif

#ifdef i_cstdio
#include <cstdio>
#endif

#ifdef i_filesystem
#include <filesystem>
#endif

#ifdef i_regex
#include <regex>
#endif

#ifdef i_atomic
#include <atomic>
#endif

#ifdef i_thread
#include <thread>
#endif

#ifdef i_mutex
#include <mutex>
#endif

#ifdef i_shared_mutex
#include <shared_mutex>
#endif

#ifdef i_future
#include <future>
#endif

#ifdef i_condition_variable
#include <condition_variable>
#endif

#ifdef i_ranges
#include <ranges>
#endif

#ifdef i_bit
#include <bit>
#endif

#ifdef i_coroutine
#include <coroutine>
#endif

#ifdef i_numbers
#include <numbers>
#endif

#ifdef i_span
#include <span>
#endif



#ifdef i_windows
#include <windows.h>
#endif

#ifdef i_windows_mal
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif


#ifdef i_std_regex
import std.regex;
#endif

#ifdef i_std_filesystem
import std.filesystem;
#endif

#ifdef i_std_memory
import std.memory;
#endif

#ifdef i_std_threading
import std.threading;
#endif

#ifdef i_std_core
import std.core;
#endif

#ifdef i_boost_variant2
#include <boost/variant2/variant.hpp>
#endif

#ifdef i_boost_optional
#include <boost/optional/optional.hpp>
#endif

#ifdef i_boost_any
#include <boost/any.hpp>
#endif


#ifdef i_date_date
#include <date/date.h>
#endif

#ifdef i_date_tz
#include <date/tz.h>
#endif


#ifdef i_tracy
#define TRACY_ENABLE
#include <tracy.hpp>
#endif

#ifdef i_spdlog
#include <spdlog/spdlog.h>
#endif

#ifdef i_fmt
#include <fmt/core.h>
#endif

#ifdef i_imgui
#include <imgui.h>
#endif

#ifdef i_nl_json
#include <nlohmann/json.hpp>
#endif

#ifdef i_nl_json_fwd
#include <nlohmann/json_fwd.hpp>
#endif

#ifdef i_ned14_outcome
#include <outcome.hpp>
#endif

#ifdef i_glm
#include <glm/glm.hpp>
#endif

#ifdef i_doctest
#include <doctest/doctest.h>
#endif

function run_meas($category, $inc, $repeats, $config)
{
   $msbuild_path = "C:\Program Files (x86)\Microsoft Visual Studio\2019\Preview\MSBuild\Current\Bin\amd64\MSBuild.exe"
   For ($i=0; $i -lt $repeats; $i++){
      Measure-Command {& $msbuild_path -verbosity:minimal -target:rebuild -property:Platform=x64 -property:Configuration=$config -p:i_$inc=1 build_project/build_project.vcxproj} | Out-File -FilePath "measurements\$category-$inc-$config.txt" -Append -Encoding utf8
   }
}

$repetitions = 10
$std_headers = "algorithm","any","array","atomic","bitset","cassert","cctype","cerrno","cfenv","cfloat","charconv","chrono","cinttypes","climits","clocale","cmath","compare","complex","concepts","condition_variable","csetjmp","csignal","cstdarg","cstddef","cstdint","cstdio","cstdlib","cstring","ctime","cuchar","cwchar","cwctype","deque","exception","execution","filesystem","forward_list","fstream","functional","future","initializer_list","iomanip","ios","iosfwd","iostream","istream","iterator","limits","list","locale","map","memory_resource","memory","mutex","new","numeric","optional","ostream","queue","random","ranges","ratio","regex","scoped_allocator","set","shared_mutex","sstream","stack","stdexcept","streambuf","string_view","string","system_error","thread","tuple","type_traits","typeindex","typeinfo","unordered_map","unordered_set","utility","valarray","variant","vector","version"
$misc_headers = "null","windows","windows_mal"

if(Test-Path measurements){
   Remove-Item measurements -Recurse
}
new-item -Name measurements -ItemType directory -Force | out-null # create measurements dir if it doesn't exist

run_meas "std" "warmup" $repetitions "Release"
Foreach($header in $misc_headers)
{
   run_meas "misc" $header $repetitions "Release"
   run_meas "misc" $header $repetitions "Debug"
}
Foreach($header in $std_headers)
{
   run_meas "std" $header $repetitions "Release"
   run_meas "std" $header $repetitions "Debug"
}

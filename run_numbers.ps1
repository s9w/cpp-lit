function Invoke-CmdScript {
  param(
    [String] $scriptName
  )
  $cmdLine = """$scriptName"" $args & set"
  & $Env:SystemRoot\system32\cmd.exe /c $cmdLine |
  select-string '^([^=]*)=(.*)$' | foreach-object {
    $varName = $_.Matches[0].Groups[1].Value
    $varValue = $_.Matches[0].Groups[2].Value
    set-item Env:$varName $varValue
  }
}

Invoke-CmdScript "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build\vcvars64.bat"



function run_meas($category, $inc, $repeats, $config)
{
   For ($i=0; $i -lt $repeats; $i++){
      Measure-Command {
         if($config -eq "Release"){
            & CL /O2 /MD /D i_$inc /std:c++latest /experimental:module /EHsc /nologo build_project/main.cpp /link /MACHINE:X64
         }
         else{
            & CL /Od /MDd /D i_$inc /std:c++latest /experimental:module /EHsc /nologo build_project/main.cpp /link /MACHINE:X64
         }
         } | Out-File -FilePath "measurements\$category-$inc-$config.txt" -Append -Encoding utf8
   }
}

$repetitions = 5
$std_headers = "algorithm","any","array","atomic","bitset","cassert","cctype","cerrno","cfenv","cfloat","charconv","chrono","cinttypes","climits","clocale","cmath","compare","complex","concepts","condition_variable","csetjmp","csignal","cstdarg","cstddef","cstdint","cstdio","cstdlib","cstring","ctime","cuchar","cwchar","cwctype","deque","exception","execution","filesystem","forward_list","fstream","functional","future","initializer_list","iomanip","ios","iosfwd","iostream","istream","iterator","limits","list","locale","map","memory_resource","memory","mutex","new","numeric","optional","ostream","queue","random","ranges","ratio","regex","scoped_allocator","set","shared_mutex","sstream","stack","stdexcept","streambuf","string_view","string","system_error","thread","tuple","type_traits","typeindex","typeinfo","unordered_map","unordered_set","utility","valarray","variant","vector","version"
$std_modules = "std_regex","std_filesystem","std_memory","std_threading","std_core"
$misc_headers = "null","windows","windows_mal"

if(Test-Path measurements){
   Remove-Item measurements -Recurse
}
new-item -Name measurements -ItemType directory -Force | out-null # create measurements dir if it doesn't exist

run_meas "std" "warmup" $repetitions "Release"
Foreach($header in $misc_headers){
   run_meas "misc" $header $repetitions "Release"
   run_meas "misc" $header $repetitions "Debug"
}
Foreach($header in $std_modules){
   run_meas "std_modules" $header $repetitions "Release"
   run_meas "std_modules" $header $repetitions "Debug"
}
Foreach($header in $std_headers){
   run_meas "std" $header $repetitions "Release"
   run_meas "std" $header $repetitions "Debug"
}

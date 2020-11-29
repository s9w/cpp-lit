# $vcvars_dir = "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build\vcvars64.bat"
$vcvars_dir = "C:\Program Files (x86)\Microsoft Visual Studio\2019\Preview\VC\Auxiliary\Build\vcvars64.bat"
$vcpkg_dir = "C:\inc\vcpkg-master"
$tracy_dir = "..\..\game\libs\tracy\tracy"

$repetitions = 10

function Invoke-CmdScript {
   param(
      [String] $script_path
   )
   Write-Output "running script $script_path"
   $cmdLine = """$script_path"" $args & set"
   & $Env:SystemRoot\system32\cmd.exe /c $cmdLine |
   select-string '^([^=]*)=(.*)$' | foreach-object {
      $varName = $_.Matches[0].Groups[1].Value
      $varValue = $_.Matches[0].Groups[2].Value
      set-item Env:$varName $varValue
   }
}
if((-Not (Test-Path env:cpp_lit_invoked_vcvars)) -And (-Not $env:cpp_lit_invoked_vcvars)){
   Invoke-CmdScript -script_path $vcvars_dir
   # prevent running that script more than once per session. It's slow and there's an issue with multiple invokations
   $env:cpp_lit_invoked_vcvars = $true
}


$include_statement = "/I" + $vcpkg_dir + "\installed\x64-windows\include " + "/I" + $tracy_dir + " "

function del_main{
   while($true){
      try{
         Remove-Item -Path main.*
         Remove-Item -Path tu*.obj
         return
      }
      catch{
         Write-Host "error, retrying" -ForegroundColor Red
      }
   }
}

function Invoke-Meas{
   Param(
      [Parameter(Mandatory=$true)] $description,
      [Parameter(Mandatory=$true)] $inc,
      [Parameter(Mandatory=$true)] $repeats,
      [Parameter(Mandatory=$true)] $include_mode
      )

   $inc_mode_str = ""
   if($include_mode -eq "all_inc"){
      $inc_mode_str = "/D all_inc"
   }
   $cl_command = "CL " + $include_statement + "/O2 /GL /Oi /MD /D NDEBUG /D " + "i_" + $inc + " " + $inc_mode_str + " /std:c++latest /experimental:module /EHsc /nologo build_project/main.cpp build_project/tu0.cpp build_project/tu1.cpp build_project/tu2.cpp build_project/tu3.cpp build_project/tu4.cpp /link /MACHINE:X64 /LTCG:incremental"
   Write-Host ("description: {0}, inc: {1}, mode: {2}" -f $description, $inc, $include_mode) -ForegroundColor DarkGreen
   
   For ($i=0; $i -lt $repeats; $i++){
      if($description -eq "warmup"){
         Invoke-Expression $cl_command | out-null
      }
      else{
         Measure-Command {
            Invoke-Expression $cl_command
         } | Out-File -FilePath "measurements\$description-$inc-$include_mode.txt" -Append -Encoding utf8
      }
      if(-Not(Test-Path "main.exe")){
         Write-Host ("no main.exe! desc: {0}, inc: {1}. Printing output, then exiting" -f $description, $inc) -ForegroundColor Red
         Invoke-Expression $cl_command
         Remove-Item -Path main.*
         exit
      }

      # Start-Sleep -s 0.5
      # Remove-Item -Path main.*
      del_main
   }
}

$std_headers = "algorithm","any","array","atomic","bitset","cassert","cctype","cerrno","cfenv","cfloat","charconv","chrono","cinttypes","climits","clocale","cmath","compare","complex","concepts","condition_variable","csetjmp","csignal","cstdarg","cstddef","cstdint","cstdio","cstdlib","cstring","ctime","cuchar","cwchar","cwctype","deque","exception","execution","filesystem","forward_list","fstream","functional","future","initializer_list","iomanip","ios","iosfwd","iostream","istream","iterator","limits","list","locale","map","memory_resource","memory","mutex","new","numeric","optional","ostream","queue","random","ranges","ratio","regex","scoped_allocator","set","shared_mutex","sstream","stack","stdexcept","streambuf","string_view","string","system_error","thread","tuple","type_traits","typeindex","typeinfo","unordered_map","unordered_set","utility","valarray","variant","vector","version"
$std_headers += "bit","coroutine","numbers","span"

$std_modules = "std_regex","std_filesystem","std_memory","std_threading","std_core"
$boost_headers = "boost_variant2","boost_optional","boost_any"

$third_party_libs = @()
$third_party_libs += "windows","windows_mal"
$third_party_libs += "date_date","date_tz"
$third_party_libs += "tracy"
$third_party_libs += "spdlog"
$third_party_libs += "fmt"
$third_party_libs += "imgui"
$third_party_libs += "nl_json_fwd","nl_json"
$third_party_libs += "ned14_outcome"
$third_party_libs += "glm"
$third_party_libs += "doctest"

# Clean measurements output dir
if(Test-Path measurements){
   Remove-Item measurements -Recurse
}
new-item -Name measurements -ItemType directory -Force | out-null

Write-Host "Start:" (get-date).ToString('T') -ForegroundColor DarkGreen

Invoke-Meas -description "warmup" -inc "warmup" -repeats $repetitions -include_mode "all_inc"

Foreach($include_mode in @('no_inc','all_inc')){
   Invoke-Meas -description "baseline" -inc "baseline" -repeats $repetitions -include_mode $include_mode
}

Foreach($header in $third_party_libs){
   Foreach($include_mode in @('no_inc','all_inc')){
      Invoke-Meas -description "third_party" -inc $header -repeats $repetitions -include_mode $include_mode
   }
}

Foreach($header in $boost_headers){
   Foreach($include_mode in @('no_inc','all_inc')){
      Invoke-Meas -description "boost" -inc $header -repeats $repetitions -include_mode $include_mode
   }
}


Foreach($header in $std_headers){
   Invoke-Meas -description "std" -inc $header -repeats $repetitions -include_mode "no_inc"
}

Foreach($header in $std_modules){
   Invoke-Meas -description "std_modules" -inc $header -repeats $repetitions -include_mode "no_inc"
}

Write-Host "End:" (get-date).ToString('T') -ForegroundColor DarkGreen

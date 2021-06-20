$vcvars_dir = "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build\vcvars64.bat"
# $vcvars_dir = "C:\Program Files (x86)\Microsoft Visual Studio\2019\Preview\VC\Auxiliary\Build\vcvars64.bat"
$vcpkg_dir = "C:\inc\vcpkg-master"
$tracy_dir = "..\..\game\libs\tracy\tracy"

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

function Setup-Tus{
   Param(
      [Parameter(Mandatory=$true)] $tu_count
   )
   For ($i=0; $i -lt $tu_count; $i++){
      Copy-Item build_project\template.cpp -Destination ("build_project\tu{0}.cpp" -f $i)
   }
}

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
      [Parameter(Mandatory=$false)] [string[]]$defines,
      [Parameter(Mandatory=$true)] $tu_count
   )

   $extra_defines_str = ""
   foreach ($d in $defines){
      $extra_defines_str += "/D " + $d + " "
   }
   $sources_str = "build_project/main.cpp"
   For ($i=0; $i -lt $tu_count; $i++){
      $sources_str += " build_project\tu{0}.cpp" -f $i
   }

   $cl_command = "CL " + $include_statement + "/O2 /GL /Oi /MD /D NDEBUG " + $extra_defines_str + " /std:c++latest /experimental:module /EHsc /nologo " + $sources_str + " /link /MACHINE:X64 /LTCG:incremental"
   
   For ($i=0; $i -lt $repeats; $i++){
      Write-Host -NoNewLine ("`rdescription: {0}, inc: {1}, defines: {2}, i:{3}/{4}" -f $description, $inc, [system.String]::Join(" ", $defines), $i, $repeats) -ForegroundColor DarkGreen
      if($description -eq "warmup"){
         Invoke-Expression $cl_command | out-null
      }
      else{
         Measure-Command {
            Invoke-Expression $cl_command
         } | Out-File -FilePath ("measurements\$description-$inc-" + $tu_count + ".txt") -Append -Encoding utf8
      }
      if(-Not(Test-Path "main.exe")){
         Write-Host ("no main.exe! desc: {0}, inc: {1}. Printing output, then exiting" -f $description, $inc) -ForegroundColor Red
         Invoke-Expression $cl_command
         del_main
         exit
      }

      del_main
   }
   Write-Host ""
}

# $std_headers = "algorithm","any","array","atomic","bit","bitset","cassert","cctype","cerrno","cfenv","cfloat","charconv","chrono","cinttypes","climits","clocale","cmath","compare","complex","concepts","condition_variable","coroutine","csetjmp","csignal","cstdarg","cstddef","cstdint","cstdio","cstdlib","cstring","ctime","cuchar","cwchar","cwctype","deque","exception","execution","filesystem","forward_list","fstream","functional","future","initializer_list","iomanip","ios","iosfwd","iostream","istream","iterator","limits","list","locale","map","memory","memory_resource","mutex","new","numbers","numeric","optional","ostream","queue","random","ranges","ratio","regex","scoped_allocator","set","shared_mutex","spa","sstream","stack","stdexcept","streambuf","string","string_view","system_error","thread","tuple","type_traits","typeindex","typeinfo","unordered_map","unordered_set","utility","valarray","variant","vector","version"
$std_headers = "filesystem"

$std_modules = "std_regex","std_filesystem","std_memory","std_threading","std_core"
# $boost_headers = "boost_variant2"
# $boost_headers = "boost_variant2","boost_optional","boost_any"

$third_party_libs = @()
# $third_party_libs += "windows","windows_mal"
# $third_party_libs += "date_date","date_tz"
# $third_party_libs += "tracy"
# $third_party_libs += "spdlog"
# $third_party_libs += "fmt"
# $third_party_libs += "imgui"
# $third_party_libs += "nl_json_fwd","nl_json"
# $third_party_libs += "ned14_outcome"
# $third_party_libs += "glm"
# $third_party_libs += "doctest"
# $third_party_libs += "boost_variant2"

# Clean measurements output dir
# if(Test-Path measurements){
#    Remove-Item measurements -Recurse
# }
new-item -Name measurements -ItemType directory -Force | out-null

Write-Host "Start:" (get-date).ToString('T') -ForegroundColor DarkGreen
Setup-Tus -tu_count 10

# Invoke-Meas -description "warmup" -inc "warmup" -repeats 5 -defines @() -tu_count 50
# Invoke-Meas -description "special" -inc "baseline" -repeats 40 -defines @("no_std") -tu_count 50
# Invoke-Meas -description "special" -inc "baseline" -repeats 40 -defines @("no_std") -tu_count 50
# Invoke-Meas -description "std" -inc "filesystem" -repeats 40 -defines @("no_std", "i_filesystem") -tu_count 1
# Invoke-Meas -description "std" -inc "filesystem" -repeats 40 -defines @("no_std", "i_filesystem") -tu_count 1

Invoke-Meas -description "warmup" -inc "warmup" -repeats 10 -defines @() -tu_count 5
# Invoke-Meas -description "special" -inc "baseline" -repeats 10 -defines @() -tu_count 5
# Invoke-Meas -description "special" -inc "baseline" -repeats 10 -defines @("i_all_std") -tu_count 1

$normal_repeat_n = 10



Foreach($header in $std_headers){
   $def = "i_{0}" -f $header
   Invoke-Meas -description "std" -inc $header -repeats $normal_repeat_n -defines @($def) -tu_count 5
}

# Foreach($header in $std_modules){
#    $def = "i_{0}" -f $header
#    Invoke-Meas -description "std_modules" -inc $header -repeats $normal_repeat_n -defines @($def) -tu_count 10
# }


# Foreach($header in $third_party_libs){
#    $def = "i_{0}" -f $header
#    Invoke-Meas -description "third_party" -inc $header -repeats $normal_repeat_n -defines @($def) -tu_count 10
#    Invoke-Meas -description "third_party" -inc $header -repeats $normal_repeat_n -defines @($def, "i_all_std") -tu_count 10
# }

Write-Host "End:" (get-date).ToString('T') -ForegroundColor DarkGreen

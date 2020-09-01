#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <regex>
#include <string>
namespace fs = std::filesystem;

namespace parser {

   double get_mean(const std::vector<double>& values) {
      const double sum = std::accumulate(values.cbegin(), values.cend(), 0.0);
      return sum / static_cast<int>(values.size());
   }

   double get_median(const std::vector<double>& values) {
      return values[values.size() / 2];
   }


   [[nodiscard]] auto get_std_dev(
      const std::vector<double>& vec,
      const double mean
   ) -> double
   {
      double squares = 0.0;
      for (const double value : vec) {
         const double term = value - mean;
         squares += term * term;
      }
      return std::sqrt(squares / (static_cast<double>(vec.size()) - 1.0));
   }


   [[nodiscard]] auto get_split_string(
      const std::string_view& s,
      const std::string_view& delimiter
   ) -> std::vector<std::string>
   {
      if (s.empty())
         return {};
      std::vector<std::string> parts;
      size_t start = 0U;
      auto end = s.find(delimiter);
      while (end != std::string::npos) {
         const std::string line = std::string(s.substr(start, end - start));
         if (!line.empty())
            parts.emplace_back(line);
         start = end + delimiter.length();
         end = s.find(delimiter, start);
      }
      const std::string line = std::string(s.substr(start, end));
      if (!line.empty())
         parts.emplace_back(line);
      return parts;
   }


   [[nodiscard]] auto replace_string(
      const std::string& str,
      const std::string& from,
      const std::string& to
   ) -> std::string
   {
      if (from.empty())
         return str;
      std::string result(str);
      size_t start_pos = 0;
      while ((start_pos = result.find(from, start_pos)) != std::string::npos) {
         result.replace(start_pos, from.length(), to);
         start_pos += to.length(); // In case 'to' contains 'from', like replacing 'x' with 'yx'
      }
      return result;
   }

   [[nodiscard]] auto get_seconds_from_file(const fs::path& path) -> std::vector<double> {
      std::vector<double> seconds;
      const std::regex pattern(R"(TotalSeconds\s*:\s*(\d*[,.]\d*))", std::regex::ECMAScript);
      std::smatch match;
      std::ifstream in_file(path);
      if (!std::filesystem::exists(path)) {
         std::cout << "Couldn't open file" << std::endl;
         return {};
      }
      std::string line;
      for (std::string line; std::getline(in_file, line); ) {
         if (std::regex_search(line, match, pattern)) {
            const std::string seconds_str = replace_string(match[1], ",", ".");
            seconds.emplace_back(std::stod(seconds_str));
         }
      }
      return seconds;
   }

   struct Measurement {
      double mean, std_dev;
   };

   struct HeaderMeasurement {
      std::string category;
      std::string header_name;
      Measurement release, debug;
   };

   auto get_measurement(const std::vector<double>& times) ->Measurement {
      const double mean = get_mean(times);
      //const double median = get_median(times);
      const double std_dev = get_std_dev(times, mean);
      return { mean, std_dev };
   }


   auto get_measurements(const fs::path& path) -> std::vector<HeaderMeasurement> {
      std::vector<HeaderMeasurement> measurements;
      for (const auto& entry : fs::directory_iterator(path)) {
         if (fs::is_directory(entry))
            continue;
         const fs::path path = entry.path();
         const Measurement measurement = get_measurement(get_seconds_from_file(path));
         const auto stem_split = get_split_string(path.stem().string(), "-");
         const std::string category = stem_split[0];
         const std::string header_name = stem_split[1];
         if (header_name == "warmup")
            continue;

         auto it = std::find_if(
            measurements.begin(),
            measurements.end(),
            [&](const HeaderMeasurement& measurement) {
               return measurement.header_name == header_name && measurement.category == category;
            }
         );
         if (it == measurements.end()) {
            measurements.emplace_back(HeaderMeasurement{ category, header_name, 0.0, 0.0 });
            it = measurements.end() - 1;
         }
         if (stem_split[2] == "Release")
            it->release = measurement;
         else
            it->debug = measurement;
      }
      return measurements;
   }


   auto get_categorized_measurements(const std::vector<HeaderMeasurement>& measurements) -> std::map<std::string, std::vector<HeaderMeasurement>> {
      std::map<std::string, std::vector<HeaderMeasurement>> sorted;
      for (const HeaderMeasurement& measurement : measurements)
         sorted[measurement.category].emplace_back(measurement);
      return sorted;
   }


   void process_files(const fs::path& input_path, const fs::path& output_folder) {
      const auto measurements = get_categorized_measurements(get_measurements(input_path));
      for (const auto& [category, measurements] : measurements) {
         fs::path output_path = output_folder / ("data_" + category + ".txt" );
         std::ofstream file_out(output_path);
         file_out << "#header_name release_mean release_stddev debug_mean debug_stddev" << std::endl;
         for (const HeaderMeasurement& measurement : measurements) {
            file_out << measurement.header_name << " ";
            file_out << measurement.release.mean << " " << measurement.release.std_dev << " ";
            file_out << measurement.debug.mean << " " << measurement.debug.std_dev;
            file_out << std::endl;
         }
      }
   }

} // parser


int main(int argc, char** argv) {
   if (argc < 2) {
      printf("too few arguments\n");
      return 0;
   }
   parser::process_files("measurements", argv[1]);
   return 0;
}

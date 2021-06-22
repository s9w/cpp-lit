import pathlib
import re
import json
from collections import defaultdict
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from collections import namedtuple
from scipy.stats import norm

Measurement = namedtuple('Measurement', ['mean', 'std'])


def get_2sigma_filtered(data):
    mu, std = norm.fit(data)
    lower = mu - 2*std
    upper = mu + 2*std
    data = data[(data < upper) & (lower < data)]
    return data


# Mean absolute deviation https://en.wikipedia.org/wiki/Average_absolute_deviation#Mean_absolute_deviation_around_the_mean
def get_MAD(data):
    mean = np.mean(data)
    return np.sum(np.abs(data-mean)) / data.size


def get_times_from_txt(filename, ignore_count):
    ms_regex = re.compile(r'TotalMilliseconds\s?:\s?(\d*[,.]\d*)')
    with open(filename) as file:
        times = np.zeros(shape=(0))
        for line in file.readlines():
            match = ms_regex.match(line.strip())
            if match is None:
                continue
            if ignore_count > 0:
                ignore_count -= 1
                continue
            ms_str = match.group(1).replace(",", ".")
            ms = float(ms_str)
            times = np.append(times, ms)
        times = get_2sigma_filtered(times)
        return times

def get_time_and_std_from_txt(filename, ignore_count):
    times = get_times_from_txt(filename, ignore_count)
    return Measurement(np.mean(times), np.std(times, dtype=np.float64))


def get_file_data(ignore_count=1):
    measurement_fn_regex = re.compile(r'([\w_]+)-([\w_]+)-(\d+)\.txt')
    file_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))
    for path in pathlib.Path('measurements').iterdir():
        if not path.is_file():
            continue
        filename = path.name
        match = measurement_fn_regex.match(filename)
        if match is None:
            continue
        category, lib, tu_count = match.group(1, 2, 3)
        if category == "std_modules":
            lib = lib.replace("std_", "std.")
        tu_count = int(tu_count)
        file_data[category][lib] = get_time_and_std_from_txt(path, ignore_count)
    # print(json.dumps(file_data, indent=4))
    return file_data


def get_pretty_name(description):
    replacements = {
        "windows": "windows.h",
         "windows_mal": "windows.h [LAM]",
         "tracy": "Tracy.cpp",
         "doctest": "doctest/doctest.h",
         "spdlog": "spdlog/spdlog.h",
         "fmt": "fmt/core.h",
         "nl_json": "nlohmann/json.hpp",
         "nl_json_fwd": "nlohmann/json_fwd.hpp",
         "glm": "glm/glm.hpp",
         "vulkan": "vulkan/vulkan.h",
         "vulkanhpp": "vulkan/vulkan.hpp"
         }
    if description in replacements.keys():
        return replacements[description]
    else:
        return description

def get_raw_labels(categories, file_data):
    labels = []
    for category in categories:
        for name in file_data[category].keys():
            labels.append(name)
    return labels

def get_labels(raw_labels):
    labels = []
    is_std = True
    for raw_label in raw_labels:
        if is_std:
            raw_label = "<{}>".format(raw_label)
        labels.append(get_pretty_name(raw_label))
        if raw_label == "<version>":
            is_std = False
    max_len = max([len(label) for label in labels])
    labels = [(label+" ").ljust(max_len+1, '—') for label in labels]
    
    return labels


def get_positions(categories, file_data):
    current_pos = 0.0
    positions = []
    for category in categories:
        for _ in file_data[category].keys():
            positions.append(current_pos)
            current_pos -= 1.0
        current_pos -= 1.0
    
    return np.array(positions)


def get_addition_error(a, b):
    return np.sqrt(a*a + b*b)

tu_count = 10
cpp_20_headers = ["concepts", "coroutines", "compare", "version", "source_location", "format", "semaphore", "span", "ranges", "bit", "numbers", "syncstream", "stop_token", "latch", "barrier"]

def get_worst(category, file_data):
    sort_data = np.empty([0, 2])
    for res in file_data[category].values():
        worst_time = (res.mean - file_data["special"]["baseline"].mean) / tu_count
        worst_time_std = get_addition_error(res.std/tu_count, file_data["special"]["baseline"].std/tu_count)
        sort_data = np.append(sort_data, np.array([[worst_time, worst_time_std]]), axis=0)
    return sort_data


def main_plot():
    file_data = get_file_data()
    categories = ["std", "std_modules", "third_party"]
    raw_labels = get_raw_labels(categories, file_data)
    labels = get_labels(raw_labels)
    positions = get_positions(categories, file_data)

    print("baseline std", file_data["special"]["baseline"].std)
    print("baseline std", file_data["std"]["algorithm"].std)

    worst_data = np.empty([0, 2])
    for category in categories:
        worst_data = np.append(worst_data, get_worst(category, file_data), axis=0)

    max_pos = np.max(np.abs(positions))
    fig = plt.figure(figsize=(10, 2 + 0.12 * max_pos))
    ax = fig.add_subplot()

    bar_height = 0.3

    _ = ax.barh(y=positions, width=worst_data[:, 0], height=bar_height, color="tab:orange")
    _ = ax.barh(y=positions, left=worst_data[:, 0] - worst_data[:, 1], width=2 * worst_data[:, 1], height=bar_height/2, color="blue", alpha=0.5)

    _ = plt.yticks(positions, labels, fontfamily="monospace", horizontalalignment='left')

    for i, label in enumerate(raw_labels):
        if label in cpp_20_headers:
            ax.get_yticklabels()[i].set_color("red")

    ax.grid(axis='x', alpha=0.2)
    ax.get_yaxis().set_tick_params(pad=130)
    ax.get_yaxis().set_tick_params(length=0)
    ax.set_axisbelow(True)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    _ = ax.axvline(x=0, linewidth=0.5, color="black", zorder=1)
    _ = ax.set_xlabel("Include time [ms]")
    ax.margins(0)
    _ = ax.set_ylim(ax.get_ylim()[0]-1, ax.get_ylim()[1]+1)

    ax2 = ax.twiny()
    _ = ax2.set_xlabel("Include time [ms]")
    ax2.set_xlim(ax.get_xlim())
    ax2.spines = ax.spines

    fig.tight_layout()
    fig.savefig("lit.png")


def disable_top_right_spines(ax):
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)


if __name__ == "__main__":
    main_plot()

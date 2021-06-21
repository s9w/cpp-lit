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


def get_file_data(mode="", ignore_count=1):
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
        if mode == "raw":
            file_data[category][lib] = get_times_from_txt(path, ignore_count)
        else:
            file_data[category][lib] = get_time_and_std_from_txt(path, ignore_count)
    # print(json.dumps(file_data, indent=4))
    return file_data


def get_labels(categories, file_data):
    labels = []
    for category in categories:
        for name in file_data[category].keys():
            labels.append(name)
    max_len = max([len(label) for label in labels])
    labels = [(label+" ").ljust(max_len+2, '—') for label in labels] #—
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
    labels = get_labels(categories, file_data)
    positions = get_positions(categories, file_data)

    print("baseline std", file_data["special"]["baseline"].std)
    print("baseline std", file_data["std"]["algorithm"].std)

    worst_data = np.empty([0, 2])
    for category in categories:
        worst_data = np.append(worst_data, get_worst(category, file_data), axis=0)

    max_pos = np.max(np.abs(positions))
    fig = plt.figure(figsize=(10, 2 + 0.15 * max_pos))
    ax = fig.add_subplot()

    bar_height = 0.3

    print("baseline", file_data["special"]["baseline"].mean)
    print("version", file_data["std"]["version"].mean)
    print("span", file_data["std"]["span"].mean)
    print("algorithm", file_data["std"]["algorithm"].mean)

    def plot_data(pos, data, bar_color, label_text):
        _ = ax.barh(y=pos, width=data[:, 0], height=bar_height, color=bar_color, label=label_text)
        _ = ax.barh(y=pos, left=data[:, 0] - data[:, 1], width=2 * data[:, 1], height=bar_height/2, color="blue", alpha=0.5)
        # _ = ax.errorbar(y=pos, x=data[:, 0], xerr=data[:, 1], capsize=3, ls="", marker=".")
        # _ = ax.scatter(y=pos, x=data[:, 0], s=5, color="black")
    plot_data(pos=positions, data=worst_data, bar_color="tab:orange", label_text="worst case")

    # ax.legend(loc="lower right")

    _ = plt.yticks(positions, labels, fontfamily="monospace", horizontalalignment='left')

    ax.grid(axis='x', alpha=0.2)
    ax.get_yaxis().set_tick_params(pad=120)
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
    # _ = ax.set_xlim(0, ax.get_xlim()[1] + 10)

    ax2 = ax.twiny()
    _ = ax2.set_xlabel("Include time [ms]")
    ax2.set_xlim(ax.get_xlim())
    ax2.spines = ax.spines

    fig.tight_layout()
    fig.savefig("lit.png")


def disable_top_right_spines(ax):
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)


def instrumentation_plot():
    file_data = get_file_data(mode="raw")
    # pick = file_data["std"]["version"]
    pick = file_data["std"]["type_traits"]
    print("pick", pick)

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(311)
    
    # histogram
    bin_counts, edges, patches = ax.hist(pick, bins=25, alpha=1.0, color="tab:blue", edgecolor='black', linewidth=0.5)
    print(np.max(bin_counts))
    mad = get_MAD(pick)
    bl = np.mean(file_data["special"]["baseline"])
    print("bl", bl)
    print("mean: {:.1f}, std: {:.1f}, MAD: {:.1f}".format((np.mean(pick)-bl)/tu_count, np.std(pick), mad))
    ax.errorbar(x=np.mean(pick), y=10, xerr=mad, marker="o", markersize=7, capsize=5, capthick=2, lw=2, color="tab:orange", label="mean and MAD error")
    
    ax.set_ylim(ymin=0)
    ax.legend()

    _ = ax.set_xlabel("Build time [ms]")
    disable_top_right_spines(ax)

    # Evolution of mean
    ax = fig.add_subplot(312)
    ax.plot(pick, ".", color="black", markersize=2, alpha=0.4)
    mean = np.zeros(shape=(0))
    std = np.zeros(shape=(0))
    for i in range(1, len(pick) + 1):
        slice = pick[:i]
        mean = np.append(mean, np.mean(slice))
        std = np.append(std, np.std(slice, dtype=np.float64))
    ax.plot(mean, label="Mean and its std up to that iteration")
    ax.fill_between(range(len(pick)), mean-std, mean+std, alpha=0.1, color="blue")

    _ = ax.set_xlabel("Iteration")
    _ = ax.set_ylabel("Build time [ms]")
    ax.set_xlim(0, len(pick))
    # ax.legend(loc="upper left")
    disable_top_right_spines(ax)
    
    # Evolution of error
    ax = fig.add_subplot(313)
    ax.plot(100.0 * std / mean)
    _ = ax.set_ylabel("Relative std [%]")
    ax.set_xlim(0, len(pick))
    disable_top_right_spines(ax)

    fig.tight_layout()
    fig.savefig("instrumentation.png")


if __name__ == "__main__":
    main_plot()
    instrumentation_plot()

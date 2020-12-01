import pathlib, re
import json
from collections import defaultdict
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


def get_ms_from_txt(filename, ignore_count=1, n=5):
    ms_regex = re.compile(r'TotalMilliseconds\s?:\s?(\d*[,.]\d*)')
    with open(filename) as f:
        times = []
        for line in f.readlines():
            match = ms_regex.match(line.strip())
            if match is None:
                continue
            if ignore_count > 0:
                ignore_count -= 1
                continue
            ms_str = match.group(1).replace(",", ".")
            ms = float(ms_str) / n
            times.append(ms)
        return np.mean(times), np.std(times)


def get_file_data():
    measurement_fn_regex = re.compile(r'([\w_]+)-([\w_]+)-([\w_]*?)\.txt')
    file_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for path in pathlib.Path('measurements').iterdir():
        if not path.is_file():
            continue
        match = measurement_fn_regex.match(path.name) #path.name returns only filename
        if match is None:
            continue
        category = match.group(1)
        lib = match.group(2)
        third = match.group(3)
        file_data[category][lib][third] = get_ms_from_txt(path)
    # print(json.dumps(file_data, indent=4))
    return file_data


def get_labels(categories, file_data):
    labels = []
    for category in categories:
        for name in file_data[category].keys():
            labels.append(name.ljust(15, '-'))
    return labels


def get_positions(categories, file_data):
    current_pos = 0.0
    positions = []
    for category in categories:
        for _ in file_data[category].keys():
            positions.append(current_pos)
            current_pos -= 1
        current_pos -= 2.0
    return np.array(positions)


def get_addition_error(a, b):
    return np.sqrt(a*a + b*b)


def get_worst(category, file_data):
    sort_data = np.empty([0, 2])
    for res in file_data[category].values():
        worst_time = res["no_std"][0] - file_data["special"]["baseline"]["no_std"][0]
        worst_time_std = get_addition_error(res["no_std"][1], file_data["special"]["baseline"]["no_std"][1])
        print("worst err", res["no_std"][1], file_data["special"]["baseline"]["no_std"][1])
        sort_data = np.append(sort_data, np.array([[worst_time, worst_time_std]]), axis=0)
    return sort_data


def get_best(category, file_data):
    sort_data = np.empty([0, 2])
    for name, res in file_data[category].items():
        baseline_all_std = file_data["special"]["baseline"]["all_std"]
        if category == "std":
            ideal_time = baseline_all_std[0] - res["no_{}".format(name)][0]
            ideal_time_std = get_addition_error(baseline_all_std[1], res["no_{}".format(name)][1])
            print("best err", baseline_all_std[1], res["no_{}".format(name)][1])
        else:
            ideal_time = res["all_std"][0] - baseline_all_std[0]
            ideal_time_std = get_addition_error(res["all_std"][1], + baseline_all_std[1])
        if category == "std_modules":
            ideal_time = 0.0
        sort_data = np.append(sort_data, np.array([[ideal_time, ideal_time_std]]), axis=0)
    return sort_data


def main():
    file_data = get_file_data()
    categories = ["std", "std_modules","third_party","boost"]
    labels = get_labels(categories, file_data)
    positions = get_positions(categories, file_data)
    # print("labels", labels)

    worst_data = np.empty([0, 2])
    for category in categories:
        worst_data = np.append(worst_data, get_worst(category, file_data), axis=0)

    best_data = np.empty([0, 2])
    for category in categories:
        best_data = np.append(best_data, get_best(category, file_data), axis=0)

    max_pos = np.max(np.abs(positions))
    fig = plt.figure(figsize=(10, 2 + 0.15 * max_pos))
    ax = fig.add_subplot()

    bar_height = 0.3
    alignment_offset = 0.05
    y_best = positions - bar_height/2.0 - 0.05 - alignment_offset
    y_worst = positions + bar_height/2.0 + 0.05 - alignment_offset

    def plot_data(pos, data, bar_color, label_text):
        _ = ax.barh(y=pos, width=data[:, 0], height=bar_height, color=bar_color, label=label_text)
        _ = ax.errorbar(x=data[:, 0], y=pos, xerr=data[:, 1], ls="", marker=".", capsize=3, capthick=2, color="black")
    plot_data(pos=y_worst, data=worst_data, bar_color="tab:orange", label_text="worst case")
    plot_data(pos=y_best, data=best_data, bar_color="limegreen", label_text="best_case")

    ax.legend(loc="lower right")

    _ = plt.yticks(positions, labels, fontfamily="monospace", horizontalalignment='left')

    ax.grid(axis='x', alpha=0.2)
    ax.get_yaxis().set_tick_params(pad=90)
    ax.get_yaxis().set_tick_params(length=0)
    ax.set_axisbelow(True)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    _ = ax.axvline(x=0, linewidth=0.5, color="black", zorder=0)
    _ = ax.set_xlabel("Include time [ms]")
    ax.margins(0)
    _ = ax.set_ylim(ax.get_ylim()[0]-1, ax.get_ylim()[1]+1)
    # _ = ax.set_xlim(0, ax.get_xlim()[1] + 10)

    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.spines = ax.spines

    fig.tight_layout()
    fig.savefig("lit.png")


if __name__ == "__main__":
    main()
    
import pathlib, re
import json
from collections import defaultdict
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


def get_ms_from_txt(filename):
    ms_regex = re.compile(r'TotalMilliseconds\s?:\s?(\d*[,.]\d*)')
    ignore_count = 1
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
            ms = float(ms_str) / 5.0 
            times.append(ms)
        return np.mean(times), np.std(times)


measurement_fn_regex = re.compile(r'([\w_]+)-([\w_]+)-([\w_]*?)\.txt')
d = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for path in pathlib.Path('measurements').iterdir():
    if not path.is_file():
        continue
    match = measurement_fn_regex.match(path.name)
    if match is None:
        continue
    category = match.group(1)
    lib = match.group(2)
    third = match.group(3)
    d[category][lib][third] = get_ms_from_txt(path)
# print(json.dumps(d, indent=4))


current_pos = 0.0

def get_sorted_data(category, labels):
    global current_pos
    sort_data = np.empty([0, 5])
    for name, res in d[category].items():
        labels.append(name.ljust(15, '-')) #—

        worst_time = res["no_std"][0] - d["special"]["baseline"]["no_std"][0]
        worst_time_std = res["no_std"][1] - d["special"]["baseline"]["no_std"][1]
        if category == "std":
            ideal_time = d["special"]["baseline"]["all_std"][0] - res["no_{}".format(name)][0]
            ideal_time_std = np.sqrt(d["special"]["baseline"]["all_std"][1]**2 + res["no_{}".format(name)][1]**2)
        else:
            ideal_time = res["all_std"] - d["special"]["baseline"]["all_std"]
            ideal_time_std = np.sqrt(res["all_std"][1]**2 + d["special"]["baseline"]["all_std"][1]**2)
        if category == "std_modules":
            ideal_time = 0.0
        sort_data = np.append(sort_data, np.array([[current_pos, worst_time, worst_time_std, ideal_time, ideal_time_std]]), axis=0)
        current_pos -= 1
    
    current_pos -= 2.0
    return sort_data

labels = []
np_data = np.empty([0, 5])
np_data = np.append(np_data, get_sorted_data("std", labels), axis=0)
np_data = np.append(np_data, get_sorted_data("std_modules", labels), axis=0)
np_data = np.append(np_data, get_sorted_data("third_party", labels), axis=0)
np_data = np.append(np_data, get_sorted_data("boost", labels), axis=0)

i_pos = 0
i_worst = 1
i_worst_std = 2
i_best = 3
i_best_std = 4

max_pos = np.max(np.abs(np_data[:,0]))
fig = plt.figure(figsize=(10, 2 + 0.15 * max_pos))
ax = fig.add_subplot()

bar_height = 0.3
y_middle = np_data[:,i_pos]
alignment_offset = 0.05
y_best = y_middle - bar_height/2.0 - 0.05 - alignment_offset
y_worst = y_middle + bar_height/2.0 + 0.05 - alignment_offset
_ = ax.barh(y=y_worst, width=np_data[:, i_worst], height=bar_height, color="tab:orange", label="worst case")
_ = ax.barh(y=y_best, width=np_data[:, i_best], height=bar_height, color="limegreen", label="best case")
_ = ax.errorbar(x=np_data[:, i_best], y=y_best, xerr=np_data[:, i_best_std], marker=".", capsize=3, capthick=2, color="black")
_ = ax.errorbar(x=np_data[:, i_worst], y=y_worst, xerr=np_data[:, i_worst_std], marker=".", capsize=3, capthick=2, color="black")
print("np_data[:, i_best_std]", np_data[:, i_best_std])
ax.legend()

_ = plt.yticks(np_data[:, i_pos], labels, fontfamily="monospace", horizontalalignment='left')

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
_ = ax.set_xlim(0, ax.get_xlim()[1] + 10)

ax2 = ax.twiny()
ax2.set_xlim(ax.get_xlim())
ax2.spines["right"].set_visible(False)
ax2.spines["top"].set_visible(False)
ax2.spines["bottom"].set_visible(False)
ax2.spines["left"].set_visible(False)

fig.tight_layout()
fig.savefig("lit.png")

import pathlib, re
import json
from collections import defaultdict
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


def get_ms_from_txt(filename):
    ms_regex = re.compile(r'TotalMilliseconds\s?:\s?(\d*[,.]\d*)')
    ignore_count = 5
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
            ms = float(ms_str)
            times.append(ms)
        times = np.array(times)

        mean = np.mean(times)
        std = np.std(times)
        return np.median(times), std


measurement_fn_regex = re.compile(r'([\w_]+)-([\w_]+)-([\w_]+)\.txt')
d = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for path in pathlib.Path('measurements').iterdir():
    
    if path.is_file():
        match = measurement_fn_regex.match(path.name)
        if match is None:
            continue
        category = match.group(1)
        lib = match.group(2)
        third = match.group(3)
        d[category][lib][third] = get_ms_from_txt(path)
# print(json.dumps(d, indent=4))


current_pos = 0.0

def get_sorted_data(category, labels, with_all_inc):
    global current_pos
    sort_data = []
    for name, res in d[category].items():
        labels.append(name)
        time = res["no_inc"][0] - d["baseline"]["baseline"]["no_inc"][0]
        time_std = res["no_inc"][1]
        if with_all_inc:
            all_inc_time = res["all_inc"][0] - d["baseline"]["baseline"]["all_inc"][0]
            all_inc_time_std = res["all_inc"][1]
            sort_data.append((time, time_std, all_inc_time, all_inc_time_std, current_pos))
        else:
            sort_data.append((time, time_std, 0, 0, current_pos - 1))
        current_pos -= 1
    if len(sort_data) == 0:
        return np.empty([5, 0])
    # sort_data.sort(key=lambda entry: entry[0])
    times, times_err, ideal_times, deal_times_err, y_pos = zip(*sort_data)
    np_data = np.vstack((y_pos, times, times_err, ideal_times, deal_times_err))
    current_pos -= 2.0
    return np_data

labels = []
np_data = np.empty([5, 0])
np_data = np.append(np_data, get_sorted_data("std", labels, with_all_inc=False), axis=1)
np_data = np.append(np_data, get_sorted_data("std_modules", labels, with_all_inc=False), axis=1)
np_data = np.append(np_data, get_sorted_data("third_party", labels, with_all_inc=True), axis=1)
np_data = np.append(np_data, get_sorted_data("boost", labels, with_all_inc=True), axis=1)



fig = plt.figure(figsize=(10, 1 + 0.15 * len(labels)))
ax = fig.add_subplot()

has_ideal = np.where(np_data[3,:] != 0)[0]
has_no_ideal = np.where(np_data[3,:] == 0)[0]

# Dashed alignment lines for all
_ = ax.hlines(y=np_data[0,:], xmin=-0.01, xmax=np_data[1,:], alpha=0.5, color="black", zorder=-1, linewidths=0.7, linestyles="dashed")

# Standard library
_ = ax.scatter(x=np_data[1,has_no_ideal], y=np_data[0,has_no_ideal], color="black")
_ = ax.errorbar(x=np_data[1,has_no_ideal], y=np_data[0,has_no_ideal], xerr=np_data[2,has_no_ideal], linestyle='None', color="black")

# Third party
_ = ax.scatter(x=np_data[1,has_ideal], y=np_data[0,has_ideal]+0.5, color="red")
_ = ax.errorbar(x=np_data[1,has_ideal], y=np_data[0,has_ideal]+0.5, xerr=np_data[2,has_ideal], linestyle='None', color="red")
_ = ax.scatter(x=np_data[3,has_ideal], y=np_data[0, has_ideal], color="limegreen")
_ = ax.errorbar(x=np_data[3,has_ideal], y=np_data[0,has_ideal], xerr=np_data[4,has_ideal], linestyle='None', color="limegreen")
_ = ax.hlines(y=np_data[0,has_ideal], xmin=np_data[1,has_ideal], xmax=np_data[3,has_ideal], alpha=0.5, color="black", zorder=-1, linewidths=3)

_ = plt.yticks(np_data[0,:], labels, fontfamily="monospace", ha='left')

ax.grid(axis='x', alpha=0.2)
ax.get_yaxis().set_tick_params(pad=110)
ax.set_axisbelow(True)
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.spines["left"].set_visible(False)

_ = ax.axvline(x=0, linewidth=0.5, color="black", zorder=0)
_ = ax.set_xlabel("Include time [ms]")
ax.margins(0)
_ = ax.set_ylim(ax.get_ylim()[0]-1, ax.get_ylim()[1]+1)
_ = ax.set_xlim(-0.01, ax.get_xlim()[1] + 10)

ax2 = ax.twiny()
ax2.set_xlim(ax.get_xlim())
ax2.spines["right"].set_visible(False)
ax2.spines["top"].set_visible(False)
ax2.spines["bottom"].set_visible(False)
ax2.spines["left"].set_visible(False)

fig.tight_layout()
fig.savefig("lit.png")
import matplotlib as mpl
import matplotlib.pyplot as plt
import os.path
import numpy as np
def get_pretty_name(name):
    if(name.startswith("std_")):
        return "std." + name[4:]
    elif(name.startswith("boost_")):
        return "boost/" + name[6:]
    elif(name.startswith("date_")):
        return "date/" + name[5:]
    return name

def get_dataset_slice(dataset, indices):
    return {
        "names": dataset["names"][indices],
        "release_mean": dataset["release_mean"][indices],
        "release_sd": dataset["release_sd"][indices],
        "debug_mean": dataset["debug_mean"][indices],
        "debug_sd": dataset["debug_sd"][indices],
        "color": dataset["color"]
    }


def load_data(fn, color, sort=True, release_baseline=0, debug_baseline=0):
    if not os.path.isfile(fn):
        return None
    comments = ["#"]
    # if baseline is supplied, ignore the baseline row itself so it doesn't get plotted
    if(debug_baseline != 0):
        comments.append("null")
    
    names = np.loadtxt(fn, delimiter=' ', unpack=False, dtype=str, ndmin=1, encoding="utf8", usecols=0, comments=comments)
    names = names.flatten().tolist() # yes, this is apparently the only way to force numby to behave like a sane person when there's only one element
    if not names:
        return None
    names = np.asarray([get_pretty_name(name) for name in names])
    release_mean, release_sd, debug_mean, debug_sd = np.loadtxt(fn, delimiter=' ', unpack=True, dtype=float, ndmin=2, usecols=[1,2,3,4], comments=comments)
    ret_value = {
        "names": names,
        "release_mean": release_mean - release_baseline,
        "release_sd": release_sd,
        "debug_mean": debug_mean-debug_baseline,
        "debug_sd": debug_sd,
        "color": color
    }
    if(sort):
        sort_data(ret_value)
    return ret_value

def sort_data(data):
    sort_indices = np.argsort(data["release_mean"]) # sort based on the mean build time of the release build
    for key in ["names", "release_mean", "release_sd", "debug_mean", "debug_sd"]:
        data[key] = data[key][sort_indices]


null_data = load_data("data_misc.txt", "white")
baseline_index = np.where(null_data["names"]=="null")
baseline_release = null_data["release_mean"][baseline_index]
baseline_debug = null_data["debug_mean"][baseline_index]

datasets = []
std_data = load_data("data_std.txt", "blue", baseline_release, baseline_debug)
std_modules_data = load_data("data_std_modules.txt", "blue", baseline_release, baseline_debug)
boost_data = load_data("data_boost.txt", "black", baseline_release, baseline_debug)
misc_data = load_data("data_misc.txt", "black", False, baseline_release, baseline_debug)

expensive_datasets = []
cheap_datasets = []
expensive_time_cutoff = 0.6
for dataset in [std_data, std_modules_data, boost_data, misc_data]:
    if dataset is None:
        continue
    exp_indices = np.where(dataset["release_mean"] > expensive_time_cutoff)
    normal_indices = np.where(dataset["release_mean"] <= expensive_time_cutoff)
    cheap_datasets.append(get_dataset_slice(dataset, normal_indices))
    if(exp_indices[0].size == 0):
        continue
    expensive_datasets.append(get_dataset_slice(dataset, exp_indices))

def create_plot(datasets, fn_prefix, mode):
    def plot_dataset(ax, y_pos, names, means, errors, colors):
        _ = ax.scatter(means, y_pos, s=40, c=colors)
        # _ = ax.errorbar(means, y_pos,xerr=errors, linestyle='none', capsize=2)
        
        _ = plt.yticks(y_pos, names, fontfamily="monospace", ha = 'left')
        ax.get_yaxis().set_tick_params(pad=110)
    
    def plot_datasets(ax, datasets, mode):
        names = []
        values = np.empty(0)
        errors = np.empty(0)
        plot_colors = []

        y_offset = 0
        y_pos = []
        
        for dataset in datasets:
            dataset_size = len(dataset["names"])
            names.extend(dataset["names"].tolist())
            y_pos.extend(range(-y_offset, -(y_offset+dataset_size), -1))
            plot_colors.extend([dataset["color"]] * dataset_size)
            values = np.append(values, dataset[mode+"_mean"])
            errors = np.append(errors, dataset[mode+"_sd"])
            y_offset += dataset_size + 1
        ax.set_xlabel("Include time [seconds]")
        ax.margins(0)
        plot_dataset(ax, y_pos, names, values, errors, plot_colors)
        ax.set_axisbelow(True)
        ax.grid(axis="y")
        ax.set_title(mode)
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.set_xlim(-0.01, ax.get_xlim()[1]+0.02)
        ax.axvline(x=0, linewidth=0.5, color="black", zorder=0)
        ax.set_ylim(ax.get_ylim()[0]-1, ax.get_ylim()[1]+1)

    number_of_entries = sum([len(dataset["names"]) for dataset in datasets])
    fig = plt.figure(figsize=(7, 1 + 0.2 * number_of_entries))
    ax = fig.add_subplot(111)
    plot_datasets(ax, datasets, mode)

    fig.tight_layout()
    fig.savefig(fn_prefix + mode +".png")

create_plot(cheap_datasets, "", "debug")
create_plot(cheap_datasets, "", "release")
create_plot(expensive_datasets, "expensive_", "debug")
create_plot(expensive_datasets, "expensive_", "release")

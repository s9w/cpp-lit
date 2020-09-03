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
        "mean": dataset["mean"][indices],
        "error": dataset["error"][indices],
        "all_mean": dataset["all_mean"][indices],
        "all_error": dataset["all_error"][indices],
        "color": dataset["color"]
    }


def load_data(fn, color, sort, baseline=0, all_baseline=0):
    if not os.path.isfile(fn):
        return None
    comments = ["#"]
    # if baseline is supplied, ignore the baseline row itself so it doesn't get plotted
    if(baseline != 0):
        comments.append("null")
    
    names = np.loadtxt(fn, delimiter=' ', unpack=False, dtype=str, ndmin=1, encoding="utf8", usecols=0, comments=comments)
    names = names.flatten().tolist() # yes, this is apparently the only way to force numby to behave like a sane person when there's only one element
    if not names:
        return None
    names = np.asarray([get_pretty_name(name) for name in names])
    mean, error, all_mean, all_error  = np.loadtxt(fn, delimiter=' ', unpack=True, dtype=float, ndmin=2, usecols=[1,2,3,4], comments=comments)
    ret_value = {
        "names": names,
        "mean": mean - baseline,
        "error": error,
        "all_mean": all_mean - all_baseline,
        "all_error": all_error,
        "color": color
    }
    if(sort):
        sort_data(ret_value)
    return ret_value

def sort_data(data):
    sort_indices = np.argsort(data["mean"])
    for key in ["names", "mean", "error", "all_mean", "all_error"]:
        data[key] = data[key][sort_indices]


null_data = load_data("data_misc.txt", "white", False)
baseline_index = np.where(null_data["names"]=="null")
baseline = null_data["mean"][baseline_index][0]
all_baseline = null_data["all_mean"][baseline_index][0]

datasets = []
std_data = load_data("data_std.txt", "blue", True, baseline, all_baseline)
std_modules_data = load_data("data_std_modules.txt", "blue", True, baseline, all_baseline)
boost_data = load_data("data_boost.txt", "red", True, baseline, all_baseline)
misc_data = load_data("data_misc.txt", "red", False, baseline, all_baseline)

expensive_datasets = []
cheap_datasets = []
expensive_time_cutoff = 0.6
for dataset in [std_data, std_modules_data, boost_data, misc_data]:
    if dataset is None:
        continue
    exp_indices = np.where(dataset["mean"] > expensive_time_cutoff)
    normal_indices = np.where(dataset["mean"] <= expensive_time_cutoff)
    cheap_datasets.append(get_dataset_slice(dataset, normal_indices))
    if(exp_indices[0].size == 0):
        continue
    expensive_datasets.append(get_dataset_slice(dataset, exp_indices))

def create_plot(datasets, fn):
    def plot_dataset(ax, y_pos, names, means, errors, colors, all_values, all_errors, bar_filter):
        y_filtered = np.array(y_pos)[bar_filter]
        all_values_filtered = all_values[bar_filter]
        width_filtered = (means-all_values)[bar_filter]
        _ = ax.barh(y_filtered, left=all_values_filtered, width=width_filtered, height=0.3, color="silver", zorder=0)
        _ = ax.scatter(means, y_pos, s=40, c=colors, zorder=2)
        _ = ax.scatter(all_values, y_pos, s=40, c="green", zorder=1)
        # _ = ax.errorbar(means, y_pos, xerr=errors, linestyle='none', capsize=2, zorder=0, color="black")
        # _ = ax.errorbar(all_values, y_pos, xerr=all_errors, linestyle='none', capsize=2, zorder=0, color="black")
        
        _ = plt.yticks(y_pos, names, fontfamily="monospace", ha = 'left')
        ax.get_yaxis().set_tick_params(pad=110)
    
    def plot_datasets(ax, datasets):
        names = []
        mean_values = np.empty(0)
        errors = np.empty(0)
        all_mean_values = np.empty(0)
        all_errors = np.empty(0)
        plot_colors = []

        y_offset = 0
        y_pos = []
        
        for dataset in datasets:
            dataset_size = len(dataset["names"])
            names.extend(dataset["names"].tolist())
            y_pos.extend(range(-y_offset, -(y_offset+dataset_size), -1))
            plot_colors.extend([dataset["color"]] * dataset_size)
            mean_values = np.append(mean_values, dataset["mean"])
            errors = np.append(errors, dataset["error"])
            all_mean_values = np.append(all_mean_values, dataset["all_mean"])
            all_errors = np.append(all_errors, dataset["all_error"])
            y_offset += dataset_size + 1
        bar_filter = np.where(all_mean_values>0)

        ax.set_xlabel("Include time [seconds]")
        ax.margins(0)
        plot_dataset(ax, y_pos, names, mean_values, errors, plot_colors, all_mean_values, all_errors, bar_filter)
        ax.set_axisbelow(True)
        ax.grid(axis="y")
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
    plot_datasets(ax, datasets)

    fig.tight_layout()
    fig.savefig(fn)

create_plot(cheap_datasets, "lit.png")
create_plot(expensive_datasets, "lit_expensive.png")

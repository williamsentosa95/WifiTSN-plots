# Import libraries
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager
import matplotlib.ticker as ticker


from scapy.all import *

BASE_SZ = 18
TEXT_COLOR = '#202020'

label_font_size = 10
axis_label_font_size = 10
marker_size = 5

def config_style():
    mpl.rcParams.update({'font.size': 10})

def __config_base_style(base_size=BASE_SZ):
    """Customize plot aesthetics."""
    mpl.rcParams['font.family'] = 'sans-serif'
    # Use a sensible *free* font.
    mpl.rcParams['font.sans-serif'] = 'Clear Sans'
    mpl.rcParams['font.size'] = base_size

    mpl.rcParams['axes.spines.top'] = False
    mpl.rcParams['axes.spines.right'] = False

    mpl.rcParams['axes.grid'] = True
    mpl.rcParams['axes.grid.axis'] = 'both'
    mpl.rcParams['axes.grid.which'] = 'both'

    mpl.rcParams['axes.edgecolor'] = '#808080'
    mpl.rcParams['axes.linewidth'] = 1.5
    mpl.rcParams['axes.titlesize'] = base_size
    mpl.rcParams['axes.labelsize'] = base_size
    mpl.rcParams['axes.labelweight'] = 'bold'

    mpl.rcParams['xtick.labelsize'] = base_size
    mpl.rcParams['xtick.color'] = '#606060'
    mpl.rcParams['xtick.major.size'] = 10
    mpl.rcParams['xtick.major.width'] = 1.5
    mpl.rcParams['xtick.minor.size'] = 6
    mpl.rcParams['xtick.minor.width'] = 1.5
    mpl.rcParams['xtick.direction'] = 'out'
    mpl.rcParams['xtick.major.pad'] = 8
    mpl.rcParams['xtick.minor.pad'] = 8

    mpl.rcParams['ytick.labelsize'] = base_size
    mpl.rcParams['ytick.color'] = '#606060'
    mpl.rcParams['ytick.major.size'] = 10
    mpl.rcParams['ytick.major.width'] = 1.5
    mpl.rcParams['ytick.minor.size'] = 6
    mpl.rcParams['ytick.minor.width'] = 1.5
    mpl.rcParams['ytick.direction'] = 'out'
    mpl.rcParams['ytick.major.pad'] = 8
    mpl.rcParams['ytick.minor.pad'] = 8

    mpl.rcParams['legend.fontsize'] = base_size
    mpl.rcParams['legend.frameon'] = True

plt.rcdefaults()
# __config_base_style()
config_style()
matplotlib.rcParams['pdf.fonttype'] = 42

def is_float(element) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False


fig, (ax1, ax2) = plt.subplots(1, 2)
base_folder = "scheduling/mean/"
base_folder2 = "scheduling/p99/"

filenames = ["CSMA_150_mean_latency.csv",
            "Dynamic_rr_mean_latency.csv",
            "RR_400_mean_latency.csv",
            "RR_2000_mean_latency.csv",
            "HBC_mean_latency.csv",
            "LLC_mean_latency.csv",
            ]

filenames_p99 = ["CSMA_150_percentile_latency.csv",
            "Dynamic_rr_percentile_latency.csv",
            "RR_400_percentile_latency.csv",
            "RR_2000_percentile_latency.csv",
            "HBC_percentile_latency.csv",
            "LLC_percentile_latency.csv",
            ]

labels = ["CSMA/CA",
        "LDRR",
        "RR, slot length = 400 $us$",
        "RR, slot length = 2000 $us$",
        "HBC",
        "LLC",
        ]

colors = [
    "tab:red", 
    "tab:blue",
    "tab:purple",
    "tab:cyan",
    "tab:brown",
    "tab:orange"
]

markers = [
    "o",
    "s",
    "s",
    "s",
    "P",
    "P",
]


# fig.set_size_inches(8, 2.5)
fig.set_size_inches(7.5, 3)
fig.subplots_adjust(top=0.8)

def process_data(fpath):
    datapoints = []
    headers = []
    line_num = 1

    textfile = open(fpath, "r")

    for line in textfile:
        if (line_num == 1): # process the header
            headers = line.strip('\n').split(',')
        else:
            entries = [float(i) for i in line.strip('\n').split(',')]  
            if (len(datapoints) == 0):
                for i in range(0, len(entries)):
                    datapoints.append([])
            for i in range(0, len(entries)):
                datapoints[i].append(entries[i])
        line_num += 1
    
    return headers, datapoints

def plot_ecdf(ax, load_times, l, color, zorder):
    x = np.sort(load_times)
    y = np.arange(len(x)) / float(len(x))
    ax.plot(x,y, label=l, linewidth=2.5, color=color, zorder=zorder) 

############ Creating plot 1 #############

for i in range(0, len(filenames)):
    data_path = base_folder + filenames[i]
    headers, datapoints = process_data(data_path)
    xvalues = [x*964*8 for x in datapoints[0]]
    yvalues = [x/1e3 for x in datapoints[1]]
    if (labels[i] == "HBC" or labels[i] == "LLC"):
        ax1.plot(xvalues, yvalues, label=labels[i], color=colors[i], linestyle="dashed")
    else:
        ax1.plot(xvalues, yvalues, label=labels[i], color=colors[i])


ax1.grid(zorder=-1)
ax1.yaxis.label.set_size(axis_label_font_size)
ax1.set(xlabel='Per-UE load ($Mbps$)')
ax1.set(ylabel='Mean latency ($ms$)')
# ax1.legend()

ax1.set_ylim([0, 35])
ax1.set_xlim([0, 60])


for i in range(0, len(filenames)):
    data_path = base_folder2 + filenames_p99[i]
    headers, datapoints = process_data(data_path)
    xvalues = [x*964*8 for x in datapoints[0]]
    yvalues = [x/1e3 for x in datapoints[1]]
    if (labels[i] == "HBC" or labels[i] == "LLC"):
        ax2.plot(xvalues, yvalues, label=labels[i], color=colors[i], linestyle="dashed")
    else:
        ax2.plot(xvalues, yvalues, label=labels[i], color=colors[i])


ax2.grid(zorder=-1)
ax2.yaxis.label.set_size(axis_label_font_size)
ax2.set(xlabel='Per-UE load ($Mbps$)')
ax2.set(ylabel='P99 latency ($ms$)')

ax2.set_ylim([0, 60])
ax2.set_xlim([0, 60])

# ax2.legend(bbox_to_anchor=(1, 1))

# ax1.xaxis.set_major_locator(plt.MultipleLocator(10))
# ax2.xaxis.set_major_locator(plt.MultipleLocator(10))
# ax1.xaxis.set_minor_locator(plt.MultipleLocator(5))
# ax2.xaxis.set_minor_locator(plt.MultipleLocator(5))


# ax1.yaxis.set_major_locator(plt.MultipleLocator(5))
# ax2.yaxis.set_major_locator(plt.MultipleLocator(5))
# ax1.yaxis.set_minor_locator(plt.MultipleLocator(5))
# ax2.yaxis.set_minor_locator(plt.MultipleLocator(5))


# # # ax1.yaxis.set_major_locator(plt.MultipleLocator(0.2))
# ax1.xaxis.set_major_locator(plt.FixedLocator([1, 10, 25, 50, 100, 200, 500, 1000]))
# ax1.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
# # # ax2.yaxis.set_major_locator(plt.MultipleLocator(0.2))
# # ax2.xaxis.set_major_locator(plt.FixedLocator([0, 10, 100, 1000]))


# # ax2.grid(zorder=-1)
# # ax2.yaxis.label.set_size(axis_label_font_size)
# # ax2.set(xlabel='Burst duration (ms)')
# # ax2.set(ylabel='CDF')
# # ax2.legend()

# # ax2.xaxis.set_major_locator(plt.MultipleLocator(10))



# # ax2.set_xlim([0, 100])
# # ax1.set_ylim([0, 0.125])
# # ax2.set_ylim([0, 0.125])
fig.legend(labels, loc="upper center", ncol = 3, fontsize=10)

# fig.tight_layout()
plt.savefig('scheduling-latency.pdf', bbox_inches='tight')

# # show plot
plt.show()


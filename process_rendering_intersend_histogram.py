# Import libraries
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager
import csv

BASE_SZ = 18
TEXT_COLOR = '#202020'

label_font_size = 10
axis_label_font_size = 10

colors = ["tab:blue"]

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

def process_data(path):
    datapoints = []
    headers = []
    line_num = 1

    textfile = open(path, "r")

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




fig, axs = plt.subplots(2, 2)
ax1 = axs[0, 0]
ax2 = axs[0, 1]
ax3 = axs[1, 0]
ax4 = axs[1, 1]
data_path_1 = "rendering/client_trace.csv"
data_path_2 = "rendering/server_trace.csv"

fig.set_size_inches(6, 4)

####### Process data ##########

headers1, datapoints1 = process_data(data_path_1)
headers2, datapoints2 = process_data(data_path_2)

########## Creating plot 1 #############

ignore_first_data = 50

intersend1 = []
values1 = [(float(i) / 1e6) for i in datapoints1[0]]
for i in range(ignore_first_data, len(values1)):
    intersend1.append(values1[i] - values1[i-1])

intersend2 = []
values2 = [(float(i) / 1e6) for i in datapoints2[0]]
for i in range(ignore_first_data, len(values2)):
    intersend2.append(values2[i] - values2[i-1])

#specify bin width to use
w=0.5

ax1.hist(intersend1, zorder=2, color=colors[0], bins=np.arange(min(intersend1), max(intersend1) + w, w))
ax2.hist(intersend2, zorder=2, color=colors[0], bins=np.arange(min(intersend2), max(intersend2) + w, w))
# plot_ecdf(ax1, intersend1, "Request", colors[0], 2)
# plot_ecdf(ax1, intersend2, "Response", colors[1], 2)

ax1.set(xlabel='Request interarrival time ($ms$)')
ax2.set(xlabel='Response interarrival time ($ms$)')
ax1.set(ylabel='Count')

ax1.grid(zorder=-1)
ax2.grid(zorder=-1)
ax1.yaxis.label.set_size(axis_label_font_size)
ax2.yaxis.label.set_size(axis_label_font_size)
ax1.set_xlim([5, 20])
ax2.set_xlim([5, 20])
ax1.set_ylim([0, 2500])
ax2.set_ylim([0, 2500])

# ax1.xaxis.set_major_locator(plt.MultipleLocator(10))
# ax1.yaxis.set_major_locator(plt.MultipleLocator(100))
# ax2.xaxis.set_major_locator(plt.MultipleLocator(10))
# ax2.yaxis.set_major_locator(plt.MultipleLocator(100))

# ########## Creating plot 2 #############
# labels = headers2
# for i in range(0, len(datapoints2)):
#     values = [(float(i)) for i in datapoints2[i]]
#     plot_ecdf(ax2, values, labels[i], colors[i], 4-i)

# ax2.set_xlim([35, 75])
# # ax2.set(ylabel='CDF')
# ax2.set(xlabel='Packet RTT (ms)')

# ax2.grid(zorder=0)     
# ax2.title.set_text('Verizon')
# ax2.xaxis.set_major_locator(plt.MultipleLocator(10))
# ax2.yaxis.set_major_locator(plt.MultipleLocator(0.2))


plt.savefig('rendering-interarrival-time-hist.pdf', bbox_inches='tight')
plt.show()
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

colors = ["tab:blue", "tab:red"]

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


fig, (ax1) = plt.subplots(1, 1)
all_data_paths = ["tcpdump/google.pcap", "tcpdump/youtube.pcap", "tcpdump/facebook.pcap"]
# data_path2 = "data/calibration/verizon-train-gap-test.csv"

client_ip = "100.64.0.2"

fig.set_size_inches(3.25, 2.75)

def process_data(data_path):
    uplink = []
    downlink = []
    base_timestamp_uplink = -1
    base_timestamp_downlink = -1
    pkts = rdpcap(data_path)
    count = 0
    for pkt in pkts:
        count += 1
        if IP in pkt:
            if pkt[IP].src == client_ip:
                if (base_timestamp_uplink < 0):
                    base_timestamp_uplink = pkt.time
                arrival_time = (pkt.time - base_timestamp_uplink)*1e3
                uplink.append((arrival_time, len(pkt)))
            elif pkt[IP].dst == client_ip:
                if (base_timestamp_uplink > 0):
                    if (base_timestamp_downlink < 0):
                        base_timestamp_downlink = pkt.time
                    arrival_time = (pkt.time - base_timestamp_downlink)*1e3
                    downlink.append((arrival_time, len(pkt)))
                
    return count, uplink, downlink

def get_interarrival_time(traces):
    inter = []
    for i in range(1, len(traces)):
        inter.append(traces[i][0] - traces[i-1][0])
    
    return inter

# def group_data(traces, threshold_ms):
#     result = []
#     curr_timestamp = traces[0][0]
#     curr_size = traces[0][1]
#     for i in range(1, len(traces)):
#         if (traces[i][0] - curr_timestamp < threshold_ms):
#             curr_size += traces[i][1]
#         else:
#             result.append((curr_timestamp, curr_size))
#             curr_timestamp = traces[i][0]
#             curr_size = traces[i][1]
    
#     result.append((curr_timestamp, curr_size))
#     return result

def group_data2(traces, threshold_ms):
    result = []
    # traces = traces[:int(0.9*len(traces))]
    curr_timestamp = traces[0][0]
    curr_size = traces[0][1]
    curr_count = 1
    for i in range(1, len(traces)):
        if (traces[i][0] - traces[i-1][0] <= threshold_ms):
            curr_size += traces[i][1]
            curr_count += 1
        else:
            start_burst = curr_timestamp
            end_burst = traces[i-1][0]
            result.append((start_burst, curr_size, curr_count, end_burst))
            curr_timestamp = traces[i][0]
            curr_count = 1
            curr_size = traces[i][1]
    
    result.append((curr_timestamp, curr_size, curr_count, traces[-1][0]))
    return result


def get_interarrival_time2(traces):
    inter = []
    for i in range(1, len(traces)):
        inter.append(float(traces[i][0] - traces[i-1][3]))
    
    return inter


def get_burst_size(traces):
    bursts = []
    for i in range(0, len(traces)):
        bursts.append(traces[i][3] - traces[i][0])
    
    return bursts

def plot_ecdf(ax, load_times, l, color, zorder):
    x = np.sort(load_times)
    y = np.arange(len(x)) / float(len(x))
    ax.plot(x,y, label=l, linewidth=2.5, color=color, zorder=zorder) 

############ Creating plot 1 #############

uplink_inter = []
downlink_inter = []
uplink_burst_size = []
downlink_burst_size = []
for data_path in all_data_paths:
    count, uplink, downlink = process_data(data_path)
    uplink = group_data2(uplink, 1)
    downlink = group_data2(downlink,1)
    # print(data_path)
    # print(downlink)
    uplink_inter = uplink_inter + get_interarrival_time2(uplink)
    downlink_inter = downlink_inter + get_interarrival_time2(downlink) 
    uplink_burst_size = uplink_burst_size + get_burst_size(uplink)
    downlink_burst_size = downlink_burst_size + get_burst_size(downlink)


print("Total count up=%d down=%d, max_up=%f, max_down=%f" % (len(uplink_inter), len(downlink_inter), np.max(uplink_inter), np.max(downlink_inter)))
# ax1.hist(uplink_inter, density=True, weights=np.ones(len(uplink_inter)) / len(uplink_inter) * 100)

# ax1.hist(uplink_inter, bins=1000, zorder=2, density=True, color=colors[0])
# ax2.hist(downlink_inter, bins=1000, zorder=2, density=True, color=colors[1])
# data = uplink_inter
# # ax1.hist(data, weights=np.ones(len(data)) / len(data))

plot_ecdf(ax1, uplink_inter, "uplink", "blue", 2)
plot_ecdf(ax1, downlink_inter, "downlink", "red", 2)

print("Uplink mean=%f, std=%f" % (np.mean(uplink_inter), np.std(uplink_inter)))
print("Downlink mean=%f, std=%f" % (np.mean(downlink_inter), np.std(downlink_inter)))

# plot_ecdf(ax2, uplink_burst_size, "uplink", "blue", 2)
# plot_ecdf(ax2, downlink_burst_size, "downlink", "red", 2)

ax1.grid(zorder=-1)
ax1.yaxis.label.set_size(axis_label_font_size)
ax1.set_xscale('log')
ax1.set(xlabel='Burst interarrival ($ms$)')
ax1.set(ylabel='CDF')
ax1.legend()

# # ax1.yaxis.set_major_locator(plt.MultipleLocator(0.2))
ax1.xaxis.set_major_locator(plt.FixedLocator([1, 3, 5, 10, 25, 50, 200, 1000]))
ax1.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
# # ax2.yaxis.set_major_locator(plt.MultipleLocator(0.2))
# ax2.xaxis.set_major_locator(plt.FixedLocator([0, 10, 100, 1000]))


# ax2.grid(zorder=-1)
# ax2.yaxis.label.set_size(axis_label_font_size)
# ax2.set(xlabel='Burst duration (ms)')
# ax2.set(ylabel='CDF')
# ax2.legend()

# ax2.xaxis.set_major_locator(plt.MultipleLocator(10))


# ax1.set_xlim([0, 100])
# ax2.set_xlim([0, 100])
# ax1.set_ylim([0, 0.125])
# ax2.set_ylim([0, 0.125])

fig.tight_layout()
plt.savefig('web-burst-interarrival.pdf', bbox_inches='tight')

# show plot
plt.show()


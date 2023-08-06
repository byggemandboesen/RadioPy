import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser()
parser.add_argument("-s", help="Sensitivity", dest="sensitivity", type=float, default=0.001)
parser.add_argument("-l", help="Line width from center freq in bins", dest="line_width", type=int, default=200)
args = parser.parse_args()
sensitivity = args.sensitivity
line_width = args.line_width

file = "observations/1420405752_24_07_2023_18_58_28.csv" # 19_23_28.csv" # 19_12_21.csv" # 19_14_38.csv"  # 19_22_07.csv" # 18_53_18.csv"
cal_file = "observations/1420405752_24_07_2023_19_31_09.csv" # 19_26_04.csv" # 19_41_40.csv" # 19_43_01.csv"  # 19_27_12.csv" # 19_32_51.csv"

data_df = pd.read_csv(file)
cal_df = pd.read_csv(cal_file)

freqs, data = data_df["Observer frame frequencies"].to_numpy(dtype=float), data_df["Data"].to_numpy(dtype=float)
cal_data = cal_df["Data"]


# For auto correction - iterate in steps of sensitivity to find suitable multiplication factor.
# Maybe also add weighting function?

# Try to find best correction in the range [-1,10] in steps of sensitivity
k = np.arange(-1, 5, sensitivity)
means = np.zeros_like(k)
bins = np.size(data)


for i in range(np.size(k)):
    calibrated = data-k[i]*cal_data
    means[i] = np.mean(np.concatenate([calibrated[:450], calibrated[650:]]))

k_min = k[np.abs(means)==np.min(np.abs(means))]
print(k_min)

fig, ax = plt.subplots(1,3, figsize=(12,6), sharex=True, sharey=True)
ax[0].step(freqs, data)
ax[1].step(freqs, cal_data)
# ax[2].plot(freqs, np.correlate(data, cal_data, "same"))
ax[2].step(freqs, data-(k_min*cal_data))

plt.tight_layout()
plt.show()

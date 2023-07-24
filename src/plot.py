import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import os

def plotData(data: np.ndarray, obs_freq: np.ndarray, rest_freq: np.ndarray, time, plot_limits = (0,0)) -> None:
    '''
    Plot the data from an observation

    data        - ndarray of observation data

    obs_freq    - observer frame frequencies

    rest_freq   - rest frame frequencies

    time        - datetime of time of observation

    plot_limits - tuple of y-axis limits (max,min)
    '''
    FS_label = 16
    FS_ticks = 12
    FS_title = 18
    FS_legend = 14
    
    # Create figure and title
    fig, ax = plt.subplots(1, 1, figsize=(9,6))
    fig.suptitle(f"Observation at: {time}", fontsize=FS_title)
    secax = ax.twiny()
    
    # Plot spectrum and format ax
    ax.step(obs_freq, data, color = "b", linewidth = 0.75, label = "Observed data")
    ax.set(xlim=(obs_freq[0], obs_freq[-1]))
    secax.set(xlim=(rest_freq[0], rest_freq[-1]))
    ax.set_xlabel(r"Observer frame frequency [$Hz$]", fontsize = FS_label)
    secax.set_xlabel(r"Rest frame frequency [$Hz$]", fontsize = FS_label)

    
    if plot_limits != (0,0):
        ax.set(ylim=plot_limits)

    # Plot 0 km/s reference line
    # ax.axvline(x = 0, color = colors.to_rgba('k', 0.5), linestyle = ':', linewidth = 1, label = 'Theoretical frequency')
    
    # Add legend, gridlines and padding
    ax.minorticks_on()
    ax.tick_params(labelsize=FS_ticks)
    secax.minorticks_on()
    secax.tick_params(labelsize=FS_ticks)
    ax.grid(alpha=0.5)
    ax.legend(fontsize=FS_legend, loc=1, fancybox=False, edgecolor="black")
    plt.tight_layout()

    # Save
    file_path = f"./observations/{time}.png"
    if not os.path.isdir("observations/"):
        os.system("mkdir observations")
    plt.savefig(file_path, dpi = 150)
    # plt.show()

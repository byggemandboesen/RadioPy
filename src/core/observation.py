from __future__ import annotations

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Observation:
    def __init__(self, dir: str) -> None:
        # TODO - Subtract data of two observations
        if not os.path.isdir(dir):
            os.mkdir(dir)
        
        self.DIR = dir.strip("/")+"/"

        self.FREQUENCY = None
        self.RADIAL_VELOCITY = None
        self.DATA = None
    
    def readInfo(self) -> dict:
        info = np.load(self.DIR+"observation_info.npz", allow_pickle=True)
        return info

    def writeInfo(self, ground_station: "GroundStation", antenna: "Antenna", sdr: "SDR") -> None:
        '''
        Write observation info to readable txt file and npz file
        '''
        az, alt = antenna.getHorizontalCoordinates(GS=ground_station)
        ra, dec = antenna.getEquatorialCoordinates(GS=ground_station)
        lon, lat = antenna.getGalacticCoordinates(GS=ground_station)

        time = ground_station.TIME
        lsr_correction = ground_station.getLSRCorrection(ra=ra, dec=dec)

        lines = [
            f"Observation time (UTC): {time}",
            f"Horizontal coordinates (az,alt): {az}, {alt}",
            f"Equatorial coordinates (ra,dec): {ra}, {dec}",
            f"Galactic coordinates (lon,lat): {lon}, {lat}",
            f"LSR correction applied (km/s): {lsr_correction}"
        ]

        with open(self.DIR+"observation_info.txt", "w") as info_file:
            for line in lines:
                info_file.write(line+"\n")
        
        np.savez(self.DIR+"observation_info.npz", time = time, horizontal_coords = np.array([az, alt]),
                equatorial_coords = np.array([ra, dec]), galactic_coords = np.array([lon, lat]), lsr_cor = lsr_correction)

    def readData(self) -> tuple:
        '''
        Return tuple of frequency, radial velocity and data
        '''
        df = pd.read_csv(self.DIR+"observation_data.csv")
        freqs, radial_vel, data = df["Frequency"], df["Radial velocity"], df["Data"]

        return np.ravel(freqs), np.ravel(radial_vel), np.ravel(data)

    def writeData(self, frequency: np.ndarray, radial_velocity: np.ndarray, data: np.ndarray) -> None:
        '''
        Write data to csv file
        '''
        self.FREQUENCY = frequency
        self.RADIAL_VELOCITY = radial_velocity
        self.DATA = data

        obs_data = {
            "Frequency": frequency,
            "Radial velocity": radial_velocity,
            "Data": data
        }
        df = pd.DataFrame(data=obs_data)

        df.to_csv(self.DIR+"observation_data.csv", encoding="utf-8", index=False)
    
    def plotData(self, plot_limits: tuple) -> None:
        '''
        Plot and save figure of data
        '''
        FS_label = 16
        FS_ticks = 12
        FS_title = 18
        FS_legend = 14
        
        # Create figure and title
        fig, ax = plt.subplots(1, 1, figsize=(9,6))
        # fig.suptitle(f"Observation: {fname}", fontsize=FS_title)
        secax = ax.twiny()
        
        # Plot spectrum and format ax
        f = self.FREQUENCY/10**6
        ax.step(f, self.DATA, color = "b", linewidth = 0.75, label = "Observed data")
        ax.set(xlim=(f[0], f[-1]))
        secax.set(xlim=(self.RADIAL_VELOCITY[0], self.RADIAL_VELOCITY[-1]))
        ax.set_xlabel(r"Observer frame frequency [$MHz$]", fontsize = FS_label)
        secax.set_xlabel(r"Radial velocity [$Km/s$]", fontsize = FS_label)

        # Set limits
        if plot_limits != (0,0):
            ax.set(ylim=plot_limits)

        # Plot 0 km/s reference line
        secax.axvline(x = 0, color = 'k', alpha=0.5, linestyle = ':', linewidth = 1, label = 'Theoretical frequency')
        
        # Add legend, gridlines and padding
        ax.minorticks_on()
        ax.tick_params(labelsize=FS_ticks)
        secax.minorticks_on()
        secax.tick_params(labelsize=FS_ticks)
        ax.grid(alpha=0.5)
        # ax.legend(fontsize=FS_legend, loc=1, fancybox=False, edgecolor="black")
        secax.legend(fontsize=FS_legend, loc=1, fancybox=False, edgecolor="black")
        plt.tight_layout()

        # Save
        file_path = self.DIR+"observation_plot.png"
        plt.savefig(file_path, dpi = 200)

import os
import shutil
from datetime import datetime
import pandas as pd
import numpy as np

import ui.config_callbacks as CB
from core.ground_station import Antenna, GroundStation
from core.soapy import SDR
import core.dsp as DSP
from core.observation import Observation, ObservationInfo, ObservationData
from plot import plotData

def runObservation():
    # Load config
    config = CB.loadConfig()
    print("Running observation...")


    # Configure Antenna/ground station
    lat = config.getfloat("Ground station", "lat")
    lon = config.getfloat("Ground station", "lon")
    elev = config.getfloat("Ground station", "elev")
    lsr_correct = config.getboolean("Ground station", "lsr_correct")
    az = config.getfloat("Ground station", "az")
    alt = config.getfloat("Ground station", "alt")
    ra = config.getfloat("Ground station", "ra")
    dec = config.getfloat("Ground station", "dec")
    use_eq_coords = config.getboolean("Ground station", "use_eq_coords")
    LO_freq = config.getfloat("Ground station", "lo_freq")

    antenna = Antenna(az, alt, ra, dec, use_eq_coords, LO_freq)
    current_time = datetime.utcnow()
    formatted_time = current_time.strftime("%d_%m_%Y_%H_%M_%S")
    gs = GroundStation(lat, lon, elev, current_time, lsr_correct, antenna)

    
    # Configure SDR
    if config.get("SDR", "driver") == "none" or config.getint("SDR", "sample_rate") == 0:
        print("Please select a driver and sample rate first!")
        return

    driver = config.get("SDR", "driver")
    sample_rate = config.getint("SDR", "sample_rate")
    PPM_offset = config.getint("SDR", "ppm_offset")
    n_bins = config.getint("SDR", "bins")
    center_freq = config.getint("SDR", "frequency")
    
    fft_num = config.getint("Spectral line", "fft_num")
    smoothing = config.getint("Spectral line", "smoothing")
    restfreq = center_freq if config.getfloat("Spectral line", "restfreq") == 0.0 else config.getfloat("Spectral line", "restfreq")*10**6

    # Determine tuning frequency
    sdr_freq = center_freq - LO_freq
    sdr = SDR(driver = driver, freq = sdr_freq, sample_rate = sample_rate, ppm_offset = PPM_offset, bins = n_bins)

    
    # Collect data
    obs_freqs, data = collectData(sdr = sdr, fft_num = fft_num, n_bins = n_bins)
    if smoothing > 0:
        data = DSP.applySmoothing(bins = data, num = smoothing)

    background_cal = config.getboolean("Spectral line", "background_cal")
    if background_cal:
        # TODO - Get cal file path, init Observation, retrieve data axis and perform cal
        pass

    # Get antenna sky coordinates
    eq_coords = antenna.getEquatorialCoordinates(gs)
    gal_coords = antenna.getGalacticCoordinates(gs)

    # Calculate radial velocities and correct for LSR if desired
    lsr_correction = gs.getLSRCorrection(ra = eq_coords[0], dec = eq_coords[1])
    radial_velocities = np.subtract([gs.freqToVel(rest_freq = restfreq, freq = freq) for freq in obs_freqs], lsr_correction)

    # Finally, plot the data
    y_limits = (config.getfloat("Spectral line", "y_min"), config.getfloat("Spectral line", "y_max"))
    plotData(data=data, obs_freq=obs_freqs, radial_vel=radial_velocities, time=formatted_time, plot_limits=y_limits)

    out_dir = config.get("Spectral line", "output_dir")
    out_dir += "" if out_dir[-1] == "/" or out_dir[-1] == "\\" else "/"
    # Save data if wanted
    if config.getboolean("Spectral line", "save_data"):
        obs_name = f"{center_freq}_{formatted_time}"

        # Create observation
        obs = Observation(dir = out_dir+obs_name+"/")
        obs.writeInfo(ground_station=gs, antenna=antenna, sdr=sdr)
        obs.writeData(fname=obs_name, frequency=obs_freqs, radial_velocity=radial_velocities, data=data)
        obs.plotData()

        # Copy config to observation folder
        shutil.copyfile("config.ini", out_dir+obs_name+"/"+"observation_config.ini")


def collectData(sdr: SDR, fft_num: int, n_bins: int) -> tuple:
    '''
    Collects and processes data from a given sdr (instance of SDR)
    Returns tuple of two arrays:

    freqs   - ndarray with frequency values

    data    - ndarray with collected data
    '''
    # Generate list with frequencies
    freqs = np.linspace(sdr.getFrequency()-sdr.getSampleRate()/2, sdr.getFrequency()+sdr.getSampleRate()/2, n_bins)
    data = np.zeros(n_bins, dtype = np.float16)
    sdr.startStream()
    try:
        for i in range(fft_num):
            data = data+DSP.doFFT(bins = sdr.readFromStream(), n_bins = n_bins)
            
        data = 10*np.log10(data/fft_num)
    except:
        print("Issue when reading bins... Please try again")
        quit()
    
    sdr.stopStream()

    # Replace bad samples lost from sample drops etc.
    idx = np.where(data==-np.inf)
    if np.size(idx) > 0:
        data[idx] = np.interp(freqs[idx], freqs, data)
        print("Bad samples replaced at:")
        print(idx[0])

    return freqs, data

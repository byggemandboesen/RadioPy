from datetime import datetime
import pandas as pd
import numpy as np

import ui.config_callbacks as CB
from processing.ground_station import Antenna, GroundStation
from processing.soapy import SDR
import processing.dsp as DSP
from processing.observation import Observation
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

    ANTENNA = Antenna(az, alt, ra, dec, use_eq_coords, LO_freq)
    current_time = datetime.utcnow()
    formatted_time = current_time.strftime("%d_%m_%Y_%H_%M_%S")
    GS = GroundStation(lat, lon, elev, current_time, lsr_correct, ANTENNA)

    
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

    autocal = config.getboolean("Spectral line", "autocal")
    if autocal:
        cal_method = config.getboolean("Spectral line", "cal_method")

        # TODO - Get cal file path, init Observation, retrieve data axis and perform cal
        

    # Get antenna sky coordinates
    eq_coords = ANTENNA.getEquatorialCoordinates(GS)
    gal_coords = ANTENNA.getGalacticCoordinates(GS)

    # Calculate radial velocities and correct for LSR if desired
    lsr_correction = GS.getLSRCorrection(ra = eq_coords[0], dec = eq_coords[1]) if lsr_correct else 0
    radial_velocities = np.subtract([GS.freqToVel(rest_freq = restfreq, freq = freq) for freq in obs_freqs], lsr_correction)

    # Finally, plot the data
    y_limits = (config.getfloat("Spectral line", "y_min"), config.getfloat("Spectral line", "y_max"))
    plotData(data=data, obs_freq=obs_freqs, radial_vel=radial_velocities, time=formatted_time, plot_limits=y_limits)

    
    # Save data if wanted
    # TODO - Find out way to store collection parameters maybe
    if config.getboolean("Spectral line", "save_data"):
        obs_data = [
            f"Observation time: {current_time}\n",
            f"Local coordinates: {az},{alt}\n",
            f"Equatorial coordinates: {eq_coords[0]},{eq_coords[1]}\n",
            f"Galactic coordinates: {gal_coords[0]},{gal_coords[1]}\n",
            f"LSR correction: {-lsr_correction}\n",
            "Data,Observer frequency,Radial velocity\n"
        ]
        
        file_name = f"observations/{center_freq}_{formatted_time}.txt"
        obs = Observation(file_name)
        obs.writeObservationFile(obs_data=obs_data, data = data, obs_freqs=obs_freqs, radial_vel=radial_velocities)


def collectData(sdr: SDR, fft_num: int, n_bins: int) -> tuple:
    '''
    Collects and processes data from a given sdr (instance of SDR)
    Returns tuple of two arrays:

    freqs   - ndarray with frequency values

    data    - ndarray with collected data
    '''
    # Generate list with frequencies
    freqs = np.linspace(sdr.getFrequency()-sdr.getSampleRate()/2, sdr.getFrequency()+sdr.getSampleRate()/2, n_bins)
    tmp_bins = np.empty(n_bins, dtype = np.complex64)
    data = np.zeros(n_bins, dtype = np.float16)
    sdr.startStream()
    try:
        for i in range(fft_num):
            tmp_bins = sdr.readFromStream()
            data = data+DSP.doFFT(bins = tmp_bins, n_bins = n_bins)
            
        data = data/fft_num
    except:
        print("Issue when reading bins... Please try again")
        quit()
    
    sdr.stopStream()

    # Replace bad samples lost from sample drops etc.
    # TODO Fix scenario where dropped sample is either first or last
    # This is especially an issue with HackRF at high sample rates
    idx = np.where(data==-np.inf)
    if np.size(idx) > 0:
        for bad_sample in idx:
            data[bad_sample] = (data[bad_sample-1]+data[bad_sample+1])/2
        print("Bad samples replaced at:")
        print(idx)

    return freqs, data

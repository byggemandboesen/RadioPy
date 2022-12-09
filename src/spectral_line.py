from datetime import datetime
import numpy as np

import ui.callbacks as CB
from ground_station import Antenna, GroundStation
from soapy import SDR
import dsp as DSP
from plot import plotData

def runObservation():
    # Apply current parameters to config
    CB.applyParameters()
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
    GS = GroundStation(lat, lon, elev, current_time, lsr_correct, ANTENNA)

    
    # Configure SDR
    if config.get("SDR", "driver") == "none" or config.getint("SDR", "sample_rate") == 0:
        print("Please select a driver and sample rate first!")
        return

    driver = config.get("SDR", "driver")
    sample_rate = config.getint("SDR", "sample_rate")
    PPM_offset = config.getint("SDR", "ppm_offset")
    bins = config.getint("SDR", "bins")
    
    fft_num = config.getint("Spectral line", "fft_num")
    median = config.getint("Spectral line", "fft_num")
    dc_offset = sample_rate/4 if config.getboolean("Spectral line", "dc_offset") and sample_rate >= 32e5 else 0
    spectral_line = config.get("Spectral line", "spectral_line")

    rest_freq, line_name = GS.parseSpectralLine(spectral_line)
    sdr_freq = rest_freq - LO_freq - dc_offset
    sdr = SDR(driver, sdr_freq, sample_rate, PPM_offset, bins)

    freqs, data = collectData(sdr, fft_num, bins, rest_freq, dc_offset)
    
    # Calculate LSR, sky coordinates and etc
    eq_coords = []


def collectData(sdr: SDR, fft_num: int, n_bins: int, rest_freq: int, dc_offset: int):
    '''
    Collects and processes data from a given sdr (instance of SDR)
    Returns tuple of two arrays:

    freqs   - ndarray with frequency values

    data    - ndarray with collected data
    '''
    # Generate list with frequencies
    freqs = np.linspace(rest_freq-sdr.getSampleRate()/2-dc_offset, rest_freq+sdr.getSampleRate()/2-dc_offset, n_bins)

    sdr.startStream()
    data = np.zeros(n_bins)
    for i in range(0,fft_num):
        tmp_bins = sdr.readFromStream()
        data = np.add(data, DSP.doFFT(tmp_bins, n_bins))
    data = np.divide(data, fft_num)
    # Sample a blank part of the spectrum
    # sdr.setFrequency(sdr_freq+1.1*sdr.getSampleRate())
    # blank = np.zeros(bins)
    # for i in range(0,fft_num):
    #     tmp_bins = sdr.readFromStream()
    #     blank = np.add(blank, dsp.doFFT(tmp_bins, bins))
    # blank = np.divide(blank, fft_num)
    # data = np.subtract(data, blank)
    sdr.stopStream()

    return freqs, data

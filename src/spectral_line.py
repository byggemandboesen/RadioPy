from datetime import datetime
import pandas as pd
import numpy as np

import ui.callbacks as CB
from ground_station import Antenna, GroundStation
from soapy import SDR
import dsp as DSP
from plot import plotData

import matplotlib.pyplot as plt

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
    GS = GroundStation(lat, lon, elev, current_time, lsr_correct, ANTENNA)

    
    # Configure SDR
    if config.get("SDR", "driver") == "none" or config.getint("SDR", "sample_rate") == 0:
        print("Please select a driver and sample rate first!")
        return

    driver = config.get("SDR", "driver")
    sample_rate = config.getint("SDR", "sample_rate")
    PPM_offset = config.getint("SDR", "ppm_offset")
    n_bins = config.getint("SDR", "bins")
    
    fft_num = config.getint("Spectral line", "fft_num")
    median = config.getint("Spectral line", "median")
    dc_offset = sample_rate/4 if config.getboolean("Spectral line", "dc_offset") and sample_rate >= 32e5 else 0
    spectral_line = config.get("Spectral line", "spectral_line")

    # Determine tuning frequency
    rest_freq, line_name = parseSpectralLine(spectral_line)
    sdr_freq = rest_freq - LO_freq - dc_offset
    sdr = SDR(driver = driver, freq = sdr_freq, sample_rate = sample_rate, ppm_offset = PPM_offset, bins = n_bins)

    
    # Collect data
    freqs, data = collectData(sdr = sdr, fft_num = fft_num, n_bins = n_bins, rest_freq = rest_freq, dc_offset = dc_offset)
    if median > 0:
        data = DSP.applyMedian(bins = data, num = median)


    # Get antenna sky coordinates
    eq_coords = ANTENNA.getEquatorialCoordinates(GS)
    gal_coords = ANTENNA.getGalacticCoordinates(GS)

    # Calculate radial velocities and correct for LSR if desired
    lsr_correction = GS.getLSRCorrection(ra = eq_coords[0], dec = eq_coords[1]) if lsr_correct else 0
    radial_velocities = np.subtract([GS.freqToVel(rest_freq = rest_freq, freq = freq) for freq in freqs], lsr_correction)

    # Finally, plot the data
    y_limits = (config.getfloat("Spectral line", "y_min"), config.getfloat("Spectral line", "y_max"))
    plotData(data, radial_velocities, line_name, gal_coords, eq_coords, lsr_correction, current_time, y_limits)

    
    # Save data if wanted
    # TODO - Find out way to store collection parameters maybe
    if config.getboolean("Spectral line", "save_data"):
        file_name = f"observations/{spectral_line.upper()}_{current_time}".replace(" ", "_")

        # Thanks to this fix
        # https://python.plainenglish.io/a-quick-trick-to-make-dataframes-with-uneven-array-lengths-32bf80d8a61d

        df_data = {
            "Data": data,
            "Velocities": radial_velocities,
            "Frequencies": freqs,
            "Eq_coords": eq_coords,
            "Gal_coords": gal_coords,
            "Spectral_line": line_name,
            "Observation_time": current_time,
            "LSR_correction": -lsr_correction
        }
        df_data = dict([(k,pd.Series(v)) for k, v in df_data.items()])
        df = pd.DataFrame(df_data)
        df.to_csv(f"{file_name}.csv", index = False)


def parseSpectralLine(line: str):
    '''
    Get the frequency and name of a given spectral line.

    Returns the frequency and name as a tuple (int: freq, str: name)
    '''
    spectral_lines = {
        "H1_1420": (1420405752, "Hydrogen, 1420MHz"),
        "OH_1612": (1612231000, "Hydroxyl, 1612MHz"),
        "OH_1665": (1665402000, "Hydroxyl, 1665MHz"),
        "OH_1667": (1667359000, "Hydroxyl, 1667MHz"),
        "OH_1720": (1720530000, "Hydroxyl, 1720MHz"),
    }

    if line.upper() not in spectral_lines.keys():
        print("Invalid line name. Please check the README for all spectral line names")
        quit()
    else:
        return spectral_lines[line.upper()]


def collectData(sdr: SDR, fft_num: int, n_bins: int, rest_freq: int, dc_offset: int):
    '''
    Collects and processes data from a given sdr (instance of SDR)
    Returns tuple of two arrays:

    freqs   - ndarray with frequency values

    data    - ndarray with collected data
    '''
    # Generate list with frequencies
    freqs = np.linspace(rest_freq-sdr.getSampleRate()/2-dc_offset, rest_freq+sdr.getSampleRate()/2-dc_offset, n_bins)
    tmp_bins = np.empty(n_bins, np.complex64)
    data = np.empty(n_bins, np.float16)
    sdr.startStream()
    try:
        for i in range(fft_num):
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
    except:
        print("Issue when reading bins... Please try again")
        quit()
    sdr.stopStream()

    return freqs, data

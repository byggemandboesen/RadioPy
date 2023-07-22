from datetime import datetime
import pandas as pd
import numpy as np

import ui.config_callbacks as CB
from processing.ground_station import Antenna, GroundStation
from processing.soapy import SDR
import processing.dsp as DSP
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
    redshift = config.getfloat("Spectral line", "redshift")
    smoothing = config.getint("Spectral line", "smoothing")

    # Determine tuning frequency
    sdr_freq = center_freq - LO_freq
    sdr = SDR(driver = driver, freq = sdr_freq, sample_rate = sample_rate, ppm_offset = PPM_offset, bins = n_bins)

    
    # Collect data
    obs_freqs, data = collectData(sdr = sdr, fft_num = fft_num, n_bins = n_bins)
    rest_freqs = GS.observerFreqToRest(freqs=obs_freqs, redshift=redshift)
    if smoothing > 0:
        data = DSP.applySmoothing(bins = data, num = smoothing)


    # Get antenna sky coordinates
    eq_coords = ANTENNA.getEquatorialCoordinates(GS)
    gal_coords = ANTENNA.getGalacticCoordinates(GS)

    # Calculate radial velocities and correct for LSR if desired
    lsr_correction = GS.getLSRCorrection(ra = eq_coords[0], dec = eq_coords[1]) if lsr_correct else 0
    radial_velocities = np.subtract([GS.freqToVel(rest_freq = center_freq, freq = freq) for freq in rest_freqs], lsr_correction)

    # Finally, plot the data
    y_limits = (config.getfloat("Spectral line", "y_min"), config.getfloat("Spectral line", "y_max"))
    plotData(data, radial_velocities, "LINE_NAME", gal_coords, eq_coords, lsr_correction, formatted_time, y_limits)

    
    # Save data if wanted
    # TODO - Find out way to store collection parameters maybe
    if config.getboolean("Spectral line", "save_data"):
        file_name = f"observations/{center_freq}_{formatted_time}"

        # Thanks to this fix
        # https://python.plainenglish.io/a-quick-trick-to-make-dataframes-with-uneven-array-lengths-32bf80d8a61d

        df_data = {
            "Data": data,
            "Observer frame frequencies": obs_freqs,
            "Rest frame frequencies": rest_freqs,
            "Radial velocity": radial_velocities,
            "Eq_coords": eq_coords,
            "Gal_coords": gal_coords,
            "Observation_time": current_time,
            "LSR_correction": -lsr_correction
        }
        df_data = dict([(k,pd.Series(v)) for k, v in df_data.items()])
        df = pd.DataFrame(df_data)
        df.to_csv(f"{file_name}.csv", index = False)


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
    data = np.empty(n_bins, dtype = np.float16)
    sdr.startStream()
    try:
        for i in range(fft_num):
            tmp_bins = sdr.readFromStream()
            data = np.add(data, DSP.doFFT(tmp_bins, n_bins))

        data = np.divide(data, fft_num)
    except:
        print("Issue when reading bins... Please try again")
        quit()
    sdr.stopStream()

    # TODO - Maybe check for blank samples and interpolate these here?

    return freqs, data

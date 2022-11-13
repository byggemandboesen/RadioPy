import numpy as np
from datetime import datetime
import argparse, json, sys, os
import pandas as pd

sys.path.append("src/")
sys.dont_write_bytecode = True
import dsp, soapy, plot
from soapy import SDR
import ui.radiopy_ui as ui
from ephemeris import Ephemeris


def main():
    parser = argparse.ArgumentParser(prog="radiopy.py", description="The python solution for radio astronomy with an SDR")
    parser.add_argument("-s", help="Quick run spectral line observation", action="store_true", dest="run_line")
    parser.add_argument("-p", help="Quick run pulsar observation", action="store_true", dest="run_pulsar")
    # parser.add_argument("-d", help="List available drivers", action="store_true", dest="list_drivers")
    # parser.add_argument("-l", help="Load, and plot, data from a given file path (csv or json)", default="none", type=str, dest="load_data")
    # parser.add_argument("-p", help="Run in pulsar mode at given frequency (in Hz)", default=0, type=int, dest="pulsar")
    args = parser.parse_args()

    if args.run_line:
        print("Running spectral line observation from config settings...")
    elif args.run_pulsar:
        print("Running pulsar observation")
    else:
        ui.runUI()
        quit()

    # if args.list_drivers:
    #     print(f"Available drivers:\n{soapy.listDrivers()}")
    #     quit()

    # Load data
    # if args.load_data != "none":
    #     file_path = args.load_data
        
    #     # Check if valid file
    #     if not os.path.isfile(file_path) or file_path[-4:] != ".csv":
    #         print("File could not be found, or it is of invalid file extension...")
    #         quit()

    #     loadData(file_path)
    #     quit()

    # Read defults from config
    with open("config.json") as config:
        parsed_config = json.load(config)
    config.close()


    # Check if pulsar module should be launched
    if parsed_config["obj"]["pulsar"]:
        print("Starting pulsar module...")
    else:
        spectralLine(parsed_config)

# TODO Redo this function
# Should make pulsar function easier to implement from SDR-, GroundStation class and corresponding params
# def spetralLine(sdr: SDR, gs: GroundStation, bins: int = 4096, fft_num: int = 1000, median: int = 0)

def spectralLine(config):
    # Create observer from config data
    lat, lon, elev = config["observer"]["lat"], config["observer"]["lon"], config["observer"]["elev"]
    az, alt = config["observer"]["az"], config["observer"]["alt"]
    current_time = datetime.utcnow()
    ephem = Ephemeris(lat, lon, elev, current_time)

    # Get frequency and initialize SDR
    # TODO Implement DC offset!!
    sdr_driver = config["sdr"]["driver"]
    sample_rate, ppm, bins = config["sdr"]["sample_rate"], config["sdr"]["PPM_offset"], config["sdr"]["bins"]
    line = config["obj"]["spectral_line"]

    # Set up DC offset/LO offset if necessary
    LO_freq = config["frontend"]["LO"]
    DC_offset = sample_rate/4 if config["sdr"]["dc_offset"] and sample_rate >= 32e5 else 0
    rest_freq, line_name = ephem.parseSpectralLine(line)
    sdr_freq = rest_freq - LO_freq - DC_offset
    
    sdr = SDR(driver = sdr_driver, freq = sdr_freq, sample_rate = sample_rate, ppm_offset = ppm, bins = bins)
    sdr.startStream()

    # Collect data
    freqs = np.linspace(rest_freq-sample_rate/2-DC_offset, rest_freq+sample_rate/2-DC_offset, bins)
    fft_num = config["sdr"]["fft_num"]

    # start = datetime.utcnow()
    data = np.zeros(bins)
    for i in range(0,fft_num):
        tmp_bins = sdr.readFromStream()
        data = np.add(data, dsp.doFFT(tmp_bins, bins))
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
    # print(f"Execution time: {datetime.utcnow()-start}")

    # TODO
    '''
    Do regular sampling and subtration to even spectrum and dc spike.
    Do FFT without checking for zero/dropped samples and without log()
    After all samples collected -> do check for 0, log()
    '''

    # Gather observation coordinates and LSR correction
    eq_coords = ephem.equatorial(alt, az)
    gal_coords = ephem.galactic(alt, az)

    velocities = [ephem.freqToVel(rest_freq, freq) for freq in freqs]
    LSR_correction = ephem.getLSRCorrection(eq_coords[0], eq_coords[1]) if config["obj"]["LSR_correct"] else 0
    if config["obj"]["LSR_correct"]:
        velocities = velocities - LSR_correction


    # Perform final DSP on data
    data = dsp.correctSlant(data)
    median = config["sdr"]["median"]
    data = dsp.applyMedian(data, int(median)) if median > 0 else data
    data = dsp.shiftNoiseFloor(data)

    # Finally, plot the data
    plot_limits = tuple(config["data"]["plot_limits"])
    plot.plotData(data, velocities, line_name, gal_coords, eq_coords, LSR_correction, current_time, plot_limits)

    # Save data in desired format
    if config["data"]["write_data"]:
        file_name = f"observations/{line.upper()}_{current_time}".replace(" ", "_")

        # Thanks to this fix
        # https://python.plainenglish.io/a-quick-trick-to-make-dataframes-with-uneven-array-lengths-32bf80d8a61d

        df_data = {
            "Data": data,
            "Velocities": velocities,
            "Frequencies": freqs,
            "Eq_coords": eq_coords,
            "Gal_coords": gal_coords,
            "Spectral_line": line_name,
            "Observation_time": current_time,
            "LSR_correction": -LSR_correction
        }
        df_data = dict([(k,pd.Series(v)) for k, v in df_data.items()])
        df = pd.DataFrame(df_data)
        df.to_csv(f"{file_name}.csv", index = False)


# TODO - This shall be done in UI
def loadData(path):
    '''
    Load data created by this software.
    Finally, the data is plotted.
    '''
    try:
        print("Loading as csv file")
        df = pd.read_csv(path)
        
        data = np.array(df["Data"])
        velocities = np.array(df["Velocities"])
        freqs = np.array(df["Frequencies"])
        eq_coords = np.array(df["Eq_coords"].dropna())
        gal_coords = np.array(df["Gal_coords"].dropna())
        line_name = df["Spectral_line"].dropna().to_string()
        current_time = df["Observation_time"].dropna().to_string()
        LSR_correction = float(-df["LSR_correction"].dropna())
    except:
        print("Error occured... Please check your file path")

    plot.plotData(data, velocities, line_name, gal_coords, eq_coords, LSR_correction, current_time)


if __name__ == "__main__":
    main()
    quit()

# TODO
# If argparse, -noui, run with default values from config.json

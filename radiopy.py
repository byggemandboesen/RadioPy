import numpy as np
from datetime import datetime
import argparse, json, sys, os
import matplotlib.pyplot as plt

sys.path.append("src/")
import dsp, soapy, plot
from soapy import SDR
import ui.radiopy_ui as ui
from ephemeris import Ephemeris


def main():
    parser = argparse.ArgumentParser(prog="radiopy.py", description="The python solution for radio astronomy with an SDR")
    # parser.add_argument("-ui", help="Run program with UI", action="store_true", dest="show_ui")
    parser.add_argument("-d", help="List available drivers", action="store_true", dest="list_drivers")
    # parser.add_argument("-p", help="Run in pulsar mode at given frequency (in Hz)", default=0, type=int, dest="pulsar")
    args = parser.parse_args()

    # if args.show_ui:
    #     ui.runUI()

    if args.list_drivers:
        print(f"Available drivers:\n{soapy.listDrivers()}")
        quit()

    # Read defults from config
    with open("config.json") as config:
        parsed_config = json.load(config)
    config.close()

    
    # Check if pulsar module should be launched
    if parsed_config["obj"]["pulsar"]:
        print("Starting pulsar module...")
    else:
        spectralLine(parsed_config)


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
    LO_freq = config["frontend"]["LO"]
    rest_freq = ephem.lineToFreq(line)
    sdr_freq = rest_freq - LO_freq
    
    sdr = SDR(driver = sdr_driver, freq = sdr_freq, sample_rate = sample_rate, ppm_offset = ppm, bins = bins)
    sdr.startStream()

    # Collect data
    freqs = np.linspace(rest_freq-sample_rate/2, rest_freq+sample_rate/2, bins)
    fft_num = config["sdr"]["fft_num"]

    data = np.zeros(bins)
    for i in range(0,fft_num):
        collected_bins = sdr.readFromStream()
        data = np.add(data, dsp.doFFT(collected_bins, bins))
    data = np.divide(data, fft_num)
    sdr.stopStream()

    # Perform DSP on data
    data = dsp.correctSlant(data)
    median = config["sdr"]["median"]
    data = dsp.applyMedian(data, int(median))
    data = dsp.shiftNoiseFloor(data)

    # Gather observation coordinates and LSR correction
    ra, dec = ephem.equatorial(alt, az)
    gal_lon, gal_lat = ephem.galactic(alt, az)

    velocities = [ephem.freqToVel(rest_freq, freq) for freq in freqs]
    LSR_correction = ephem.getLSRCorrection(ra, dec) if config["obj"]["LSR_correct"] else 0
    if config["obj"]["LSR_correct"]:
        velocities = velocities - LSR_correction

    plot.plotData(data, velocities, [gal_lon, gal_lat], [ra, dec], LSR_correction, current_time)

    # Finally, plot the data
    # plt.plot(velocities, data)
    # plt.show()


if __name__ == "__main__":
    main()
    quit()


# TODO
# If argparse, -noui, run with default values from config.json


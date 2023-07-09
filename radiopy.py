import numpy as np
from datetime import datetime
import argparse, json, sys, os
import pandas as pd

sys.path.append("src/")
sys.dont_write_bytecode = True
import ui.radiopy_ui as ui

from spectral_line import runObservation


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
        runObservation()
    elif args.run_pulsar:
        print("Running pulsar observation")
    else:
        ui.runUI()
    quit()

if __name__ == "__main__":
    main()

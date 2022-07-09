# RadioPy
A software solution for scientific radio astronomy with an SDR

## Installing
RadioPy uses the python bindings for the SoapySDR environment.<br>
To install these run the following in terminal:
```bash
sudo apt install swig
sudo apt install python3-soapysdr
```

This will install the python bindings globally, so if you want to access them in a virtual environment, you will need to specify, that you wish to include global packages.
```bash
python3 -m venv --system-site-packages venv
```
Then the virtual environment, `venv`, can be activated as usual.<br>

To install the rest of the required packages, simply use pip.
```bash
pip3 install -r requirements.txt
```

### Windows (:cold_sweat:)
Since RadioPy uses python bindings it should be cross platform, however, it may involve a lot of pain setting up the Soapy environment properly on Windows. For this reason, I will only point you to Soapy's own guide to [using/installing the python bindings](https://github.com/pothosware/SoapySDR/wiki/PythonSupport).

## Usage
The primary goal for RaioPy is to act as a simple, yet useful, tool for radioastronomy. This means it offers a way to perform observations of different radioastronomical spectral lines with numerous different SDR's.

### Tested devices
* RTL-SDR V3.0
* Nooelec XTR
* Airspy mini
* HackRF
This list will likely grow as users report their experience with different devices!

### Performing observation
The software can be used headless through terminal with the help of the configuration file, `config.json`, or with the optional UI which can be accessed with the `-ui` command line argument.
```bash
python3 radiopy.py -ui
```

If you chose to edit the config file manually, here's a breif description of all the features/settings.
```json
{
    "observer": {
        "lat": 0.0,
        "lon": 0.0,
        "elev": 20,
        "az": 0.0,
        "alt": 0.0
    },
    "obj": {
        "pulsar": false,
        "spectral_line": "H1",
        "LSR_correct": true
    },
    "sdr": {
        "driver": "rtlsdr",
        "sample_rate": 2400000,
        "PPM_offset": 0,
        "bins": 4096,
        "fft_num": 1000,
        "median": 10,
        "dc_offset": true
    },
    "frontend": {
        "LO": 0
    },
    "data": {
        "plot_limits": [0,0],
        "write_data": false,
        "type": "csv"
    }
}
```
The `observer` section includes information about the geographic location of the antenna/receiver together with the horizontal coordinates of the antenna.<br>
The `obj` section includes information about the type of object being observed. Please note, the pulsar feature is not implementet yet! A list of spectral lines can be found here:
* H1 - Hydrogen, 1420MHz
* OH_1612 - Hydroxyl, 1612MHz
* OH_1665 - Hydroxyl, 1665MHz
* OH_1667 - Hydroxyl, 1667MHz
* OH_1720 - Hydroxyl, 1720MHz
This list will most likely also include more spectral lines in the future. <br>
The `sdr` section includes settings for the SDR and data collection for observing a given spectral line. The `dc_offset` offsets the center frequency by a quarter of the sample rate, so the center frequency is not disturbed by the DC spike from some devices. <br>
The `frontend` section includes an optional downconversion frequency if you're using a local oscillator. This may be usefult for observing higher frequencies like water masers. <br>
Finally, the `data` section allows the user to define the visible y-axis range for the observation plot and to save the data from the observation in either a `json` or `csv` file. <br>

In the future, I hope to include a module for pulsar observation as well.

# TODO
* Pulsar module
* Improve sampling method
* Create UI
* Improve README
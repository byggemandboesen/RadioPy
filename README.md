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
The software is mainly designed to be used through the UI, but can also be run through terminal with the help of the configuration file, `config.ini`. To run a quick spectral line observation through the terminal, run:
```bash
python3 radiopy.py -s
```

Below, a breif description of all the parameters in the `config.ini` file can be found.
```ini
[Ground station]
lat = 0                     # [float] Latitude of ground station
lon = 0                     # [float] Lonitude of ground station
elev = 20                   # [float] Elevation ASL for ground station in meters
lsr_correct = True          # [bool]  Correct for LSR (Local Standard of Rest)
az = 0                      # [float] Azimuth of antenna
alt = 0                     # [float] Altitude of antenna
ra = 0                      # [float] Right ascension of antenna
dec = 0                     # [float] Declination of antenna
use_eq_coords = False       # [bool]  Use equatorial coordinates for antenna
lo_freq = 0                 # [float] Optional LO frequency for downconverters

[SDR]   
driver = none               # [str]   SDR driver to use
sample_rate = 0             # [float] Sample rate of SDR
ppm_offset = 0              # [float] PPM offset of SDR
bins = 4096                 # [float] Bins per FFT

[Spectral line] 
fft_num = 1000              # [float] Number of FFTs to average
median = 0                  # [float] Bins to include in median smoothing
dc_offset = False           # [bool]  Offset center frequency to avoid DC spike overlap
spectral_line = H1_1420     # [str]   Spectral line to observe
y_min = 0.0                 # [float] y-axis minimum
y_max = 0.0                 # [float] y-axis maximum
save_data = False           # [bool] Export observation data as csv file
```
**Thorough description of config parameters coming soon**
A list of spectral lines can be found here:
* H1_1420 - Neutral hydrogen, 1420MHz
* OH_1612 - Hydroxyl, 1612MHz
* OH_1665 - Hydroxyl, 1665MHz
* OH_1667 - Hydroxyl, 1667MHz
* OH_1720 - Hydroxyl, 1720MHz

This list will most likely also include more spectral lines in the future. <br>
In the future, I hope to include a module for pulsar observation as well.

# TODO
* Pulsar module
* Create UI
* Improve README
* Add FITS support
* Make UI main way of use
* Make separate processing parameters for pulsar/spetral line
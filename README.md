# RadioPy
A software solution for scientific radio astronomy with an SDR

## Installing
RadioPy uses the python bindings for the SoapySDR environment.<br> This section discribes the installation of Soapy and other dependencies for both Linux and Windows

### Linux
SoapySDR is installed through apt together with swig, which is required by the pothos environment.
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

### Windows
Download the pothos environment following [the following link](https://downloads.myriadrf.org/builds/PothosSDR/). <br>
Next, add ```<YOUR INSTALL PATH>\PothosSDR\bin``` to system path.

### Additions
Finally, at least on Windows, Soapy is only compatible with Python 3.9.

Furthermore, run ```volk_profile``` for optimised performance.

## Usage
The primary goal for RaioPy is to act as a simple, yet useful, tool for radioastronomy. This means it offers a way to perform observations of different radioastronomical spectral lines with numerous different SDR's.

### Tested devices (Outdated list)
| Device                  | Tested | Buggy | Remarks                                                                                                                              |
|-------------------------|--------|-------|--------------------------------------------------------------------------------------------------------------------------------------|
| RTL-SDR V3              | ✅      | No    | None                                                                                                                                 |
| RTL-SDR V4              | ⛔      |       |                                                                                                                                      |
| Nooelec NESDR SMArt v5  | ⛔      |       |                                                                                                                                      |
| Nooelec NESDR SMArt XTR | ✅      | Yes   | Some sample rates are not usable (usually low sample rates)                                                                          |
| Airspy mini             | ✅      | No    | During testing, it has been experienced that the Airspy mini easily disconnects from the PC if not secured properly in the USB port. |
| Airspy R2               | ⛔      |       |                                                                                                                                      |
| HackRF                  | ✅      | Yes   | It seems that the highest achievable sample rate greatly depends on the USB port/PC you're using the device with                     |
| Blade RF                | ⛔      |       |                                                                                                                                      |


This list will likely grow as users report their experience with different devices!<br>
#### Quick note about the HackRF and Airspy mini
I'm still trying to figure out the reason behind this, but for now I've only been able to do 15MSPS on my main PC and 7MSPS on my older laptop hence my remark shown in the table. However, this will need further investigation. <br>
I've also yet to figure out the reason behind the garbage samples it sometimes delivers. I rarely experience this on my main PC where I can usually fix it by running a couple observations. <br>

With the Airpsy mini I have encountered a bug on my laptop, where it's *missing a driver*. I have yet to find out the reason behind this, as I've never experienced it on my main PC.

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
bins = 1024                 # [float] Bins per FFT
frequency = 1420405752      # [int]   Center frequency

[Spectral line] 
fft_num = 1000              # [float] Number of FFTs to average
median = 0                  # [float] Bins to include in median smoothing
restfreq = 0.0              # [float] Rest frequency of desired line feature
y_min = 0.0                 # [float] y-axis minimum
y_max = 0.0                 # [float] y-axis maximum
save_data = True            # [bool]  Export observation data as csv file
autocal = False             # [bool]  Calibrate observation during collection
cal_method = Autocalibrate  # [str]   Method of calibration
```
**Thorough description of config parameters coming soon**
The frequency can be set from a certain number of spectral line presets:
* H1, 1420 - Neutral hydrogen, 1420MHz
* OH, 1612 - Hydroxyl, 1612MHz
* OH, 1665 - Hydroxyl, 1665MHz
* OH, 1667 - Hydroxyl, 1667MHz
* OH, 1720 - Hydroxyl, 1720MHz

This list will most likely also include more spectral lines in the future. <br>
In the future, I hope to include a module for pulsar observation as well.

# TODO
* Somehow save observation parameters for each observation
* Spectral line data editor/viewer
* Improve README
* Add calibration from frequency offset observation or from observation file
* *Pulsar module*
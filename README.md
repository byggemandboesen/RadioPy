# RadioPy
A software solution for scientific radio astronomy with an SDR


To install SoapySDR:
```bash
sudo apt install swig
sudo apt install python3-soapysdr
```

To use global install of SoapySDR:


```bash
python3 -m venv --system-site-packages venv
```


# TODO
* Pulsar module
* Implement more spectral lines together with masers
* Consider implementing DC offset
    - Set limit for sample rate, eg. DC offset not prossible for sample rates below or equal to 3.2MSPS (to include RTL)
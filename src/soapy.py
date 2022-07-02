import SoapySDR
from SoapySDR import *

import numpy as np

def listDrivers():
    '''
    Retreive the available Soapy drivers.

    The available drivers are returned as a list of strings
    '''

    soapy_drivers = [dict(item) for item in SoapySDR.Device.enumerate()]
    driver_names = [driver["driver"] for driver in soapy_drivers if driver["driver"] != "audio"]
    return driver_names


class SDR():
    def __init__(self, driver: str, freq: int = 1420405752, sample_rate: int = 1e6, ppm_offset: int = 0, bins: int = 4096):
        
        # Initialize SDR
        self.center_frequency = freq
        self.sample_rate = sample_rate
        self.ppm_offset = ppm_offset
        self.bins = bins
        
        self.sdr = SoapySDR.Device(f"driver={driver}")
        # Set automatic gain
        self.sdr.setGainMode(SOAPY_SDR_RX, 0, True)
        self.setSampleRate(sample_rate)
        self.setFrequency(freq)
        self.setPPMOffset(ppm_offset)
        
        # Initialize variables for later use
        self.buffer = np.array([0]*bins, np.complex64)
        self.rxStream = None

    # ------------------------------ Properties ------------------------------ #

    def getAvailableFreqencyRange(self):
        '''
        Get the tunable frequency range for the current SDR
        Returns a list of lowest and highest tunable frequency
        '''
        range = self.sdr.getFrequencyRange(SOAPY_SDR_RX, 0)[0]
        return [range.minimum(), range.maximum()]
    
    def getAvailableSampleRates(self):
        '''
        Get the tunable sample rates for the current SDR
        Returns a list of tunable sample rates
        '''
        range = self.sdr.listSampleRates(SOAPY_SDR_RX, 0)
        return list(range)
    
    def getTunableElements(self):
        '''
        Get the tunable elements (RF and sometimes PPM correction)
        Returns a list of tunable elements
        '''
        elem = self.sdr.listFrequencies(SOAPY_SDR_RX, 0)
        return list(elem)


    def setFrequency(self, frequency: int):
        '''
        Set the center frequency to a given frequency
        '''
        avail_freqs = self.getAvailableFreqencyRange()
        if avail_freqs[0] < frequency and frequency < avail_freqs[1]:
            self.sdr.setFrequency(SOAPY_SDR_RX, 0, frequency)
        else:
            print("Frequency is outside the range of this device!!")
            quit()

    def getFrequency(self):
        '''
        Return the current center frequency
        '''
        return self.sdr.getFrequency(SOAPY_SDR_RX, 0)


    def setSampleRate(self, sample_rate: int):
        '''
        Set the sample rate to a given sample rate
        '''
        try: # sample_rate in self.getAvailableSampleRates():
            self.sdr.setSampleRate(SOAPY_SDR_RX, 0, sample_rate)
        except:
            print("Device does not support the selected sample rate!!")
            quit()

    def getSampleRate(self):
        '''
        Return the current sample rate
        '''
        return self.sdr.getSampleRate(SOAPY_SDR_RX, 0)

    
    def setBins(self, bins: int):
        '''
        Set the number of bins collected to the buffer wehn streaming
        '''
        # Do hacky integer evaluation
        if np.log2(bins) % 1 == 0 and bins > 0:
            self.bins = bins
            self.buffer = np.array([0]*bins, np.complex64)
        else:
            print("Invalid number of bins. Must be positive and follow exponential with base 2 and an integer power!!")
            quit()

    def getBins(self):
        '''
        Return the current number of bins collected when reading from stream
        '''
        return self.bins


    def setPPMOffset(self, offset: int):
        '''
        Set the PPM offset for the SDR
        '''
        if "CORR" in self.getTunableElements():
            try:
                self.sdr.setFrequencyCorrection(SOAPY_SDR_RX, 0, offset)
            except Exception as e:
                raise Exception(e)
        else:
            print("PPM offset not availabe for this device... skipping...")
    
    def getPPMOffset(self):
        '''
        Return the current PPM offset
        '''
        return self.sdr.getFrequencyCorrection(SOAPY_SDR_RX, 0)


    # ------------------------------- Streaming ------------------------------ #

    def startStream(self):
        '''
        Start a stream from device
        '''
        self.rxStream = self.sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
        self.sdr.activateStream(self.rxStream)

    def readFromStream(self):
        '''
        Read bins into buffer
        '''
        if self.rxStream == None:
            print("Stream has not been started yet. Please run startStream() first!!")
            quit()
        
        sr = self.sdr.readStream(self.rxStream, [self.buffer], self.bins)
        if sr.ret < self.bins:
            print(f"Error when reading samples... Received {sr.ret}, but expected {self.bins}")
            quit()
        return self.buffer

    def stopStream(self):
        '''
        Stop the stream from device
        '''
        if self.rxStream == None:
            print("No stream to stop. Please start a stream with startStream()!!")
            quit()

        self.sdr.deactivateStream(self.rxStream)
        self.sdr.closeStream(self.rxStream)
        self.rxStream = None


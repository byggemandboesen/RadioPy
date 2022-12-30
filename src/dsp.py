import numpy as np

def doFFT(bins, n_bins: int):
    '''
    Perform FFT on the given bins
    '''
    PSD = (np.abs(np.fft.fft(bins))/n_bins)**2
    PSD = checkForZero(PSD)
    PSD_log = 20.0*np.log10(PSD)
    fft_bins = np.fft.fftshift(PSD_log)
    return fft_bins


def checkForZero(bins):
    '''
    Replace dropped samples with mean of neighbors
    '''
    index = np.array(np.where(bins == 0))
    if index.size == 0:
        return bins
    print('Dropped sample was recovered!')
    bins[index] = np.mean(bins[index+1]+bins[index-1])
    # TODO Fix scenario where dropped sample is either first or last
    # This is especially an issue with HackRF at high sample rates
    return bins


def applyMedian(bins, num: int = 10):
    '''
    Perform median smoothing on the given bins
    '''
    n_bins = len(bins)
    for i in range(n_bins):
        bins[i] = np.mean(bins[i:i+num])
    return bins


def correctSlant(bins):
    '''
    Correct for any linear slope in the noise floor
    '''
    X = np.linspace(0,len(bins) - 1, len(bins))
    slope, intersect = np.polyfit(X, bins, 1)
    bins = np.array([bins[i] - (intersect + i * slope) for i in range(len(X))])
    return bins


def shiftNoiseFloor(bins):
    '''
    Shift the noise floor to 0 dB
    '''
    offset = np.mean(bins)
    return bins - offset


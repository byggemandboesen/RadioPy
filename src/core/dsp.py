import numpy as np

def doFFT(bins, n_bins: int):
    '''
    Perform FFT on the given bins
    '''
    PSD = (np.abs(np.fft.fft(bins))/n_bins)**2
    PSD_log = 10.0*np.log10(PSD)
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
    
    return bins


def applySmoothing(bins, num: int = 10):
    '''
    Perform median smoothing on the given bins
    '''
    return np.convolve(bins, np.ones(num)/num, 'same')


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


import numpy as np

def doFFT(bins, n_bins: int):
    '''
    Perform FFT on the given bins
    '''
    PSD = (np.abs(np.fft.fft(bins))/n_bins)**2
    fft_bins = np.fft.fftshift(PSD)
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


def applySmoothing(bins, num: int = 15):
    '''
    Perform median smoothing on the given bins

    Smoothing factor must be odd number for padding to work
    '''
    if num%2==0:
        print("Smoothing factor must be odd!")
        return bins

    padded = np.pad(bins, pad_width=int((num-1)/2), mode="reflect")
    return np.convolve(padded, np.ones(num)/num, "valid")


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


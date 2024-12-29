from dataclasses import dataclass
import numpy as np
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, LSRK, EarthLocation, AltAz, ICRS, Galactic

# Suppress warnings
import warnings
from astropy.utils.exceptions import AstropyWarning
warnings.simplefilter('ignore', category=AstropyWarning)

@dataclass
class Antenna:
    '''
    Antenna object containing the following parameters
    Antenna direction in the sky
     - AZ
     - ALT
     - RA
     - DEC
    use_eq_coords       Use equatorial coordinates of antenna position (ra, dec)
    LO_FREQ             Frequency of local oscillator in Hz
    '''
    AZ: float
    ALT: float
    RA: float
    DEC: float
    use_eq_coords: bool
    LO_FREQ: float
    

    def getHorizontalCoordinates(self, GS) -> tuple:
        '''
        Return horizontal coordinates of antenna direction.

        Takes the respective ground station as argument (instance of GroundStation)

        Returns (az, alt)
        '''
        if not self.use_eq_coords:
            return [self.AZ, self.ALT]
        
        # Defines GS QTH
        altaz = AltAz(obstime = GS.TIME, location = GS.QTH, pressure = 0*u.bar)
        # Defines sky-coordinate in equatorial coords
        eq_coord = ICRS(ra=self.RA*u.degree, dec=self.DEC*u.degree)
        # Convert
        horizontal_coord = eq_coord.transform_to(altaz)

        return horizontal_coord.az.degree, horizontal_coord.alt.degree
        

    def getEquatorialCoordinates(self, GS) -> tuple:
        '''
        Return equatorial coordinates of antenna direction.

        Takes the respective ground station as argument (instance of GroundStation)

        Returns (ra, dec)
        '''
        if self.use_eq_coords:
            return [self.RA, self.DEC]
        
        # Define horizontal coordinates
        horizontal_coord = AltAz(alt = self.ALT*u.degree, az = self.AZ*u.degree, pressure = 0*u.bar, obstime = GS.TIME,location=GS.QTH)
        # Convert
        eq_coord = SkyCoord(horizontal_coord.transform_to(ICRS()))

        return eq_coord.ra.degree, eq_coord.dec.degree
    

    def getGalacticCoordinates(self, GS) -> tuple:
        '''
        Return galactic coordinates of antenna direction.

        Takes the respective ground station as argument (instance of GroundStation)

        Returns (lon (l), lat (b))
        '''
        # Define local horizontal coordinate
        az_alt = self.getHorizontalCoordinates(GS)
        horizontal_coord = AltAz(alt = az_alt[1]*u.degree, az = az_alt[0]*u.degree, pressure = 0*u.bar, obstime = GS.TIME,location=GS.QTH)
        # Convert
        gal_coord = horizontal_coord.transform_to(Galactic())

        return gal_coord.l.degree, gal_coord.b.degree


class GroundStation:
    def __init__(self, lat: float, lon: float, elev: float, time, lsr_correct: bool, antenna: Antenna):
        self.QTH = EarthLocation(lat = lat*u.degree, lon=lon*u.degree,height=elev*u.m)
        self.TIME = Time(time)
        self.lsr_correct = lsr_correct

    
    def freqToVel(self, rest_freq, freq) -> float:
        '''
        Compute radial velocity from frequency

        OBS!! Note the negative sign on the radial velocity due to astropy calculating doppler
        '''
        spectral_freq = u.doppler_radio(rest_freq*u.Hz)
        measured = freq*u.Hz
        radial_vel = -measured.to(u.km/u.s,equivalencies=spectral_freq)

        return radial_vel.value


    def velToFreq(self, rest_freq, radial_vel) -> float:
        '''
        Compute frequency from radial velocity

        OBS!! Note the negative sign on the radial velocity due to astropy calculating doppler
        '''
        spectral_freq = u.doppler_radio(rest_freq*u.Hz)
        measured = -radial_vel*u.km/u.s
        freq = measured.to(u.Hz,equivalencies=spectral_freq)

        return freq.value
    

    def observerFreqToRest(self, freqs: "np.ndarray | float", redshift: float) -> "np.ndarray | float":
        '''
        Convert observed frequency to rest frame frequency
        '''
        return freqs*(1+redshift)


    def restFreqToObserver(self, freqs: "np.ndarray | float", redshift: float) -> "np.ndarray | float":
        '''
        Convert rest frame frequency to observer frequency
        '''
        return freqs/(1+redshift)


    def getLSRCorrection(self, ra, dec) -> float:
        '''
        Compute the necessary velocity correction for LSR reference frame
        '''
        if not self.lsr_correct:
            return 0
        
        sky_coord = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame="icrs")
        # Correction wrt. barycenter
        bary_corr = sky_coord.radial_velocity_correction(obstime = self.TIME, location = self.QTH)
        # Transform to km/s
        bary_corr = bary_corr.to(u.km/u.s)
        # Finally, correction wrt. LSR
        obs_wrt_bary = ICRS(ra=ra*u.degree, dec=dec*u.degree, pm_ra_cosdec=0*u.mas/u.yr, pm_dec=0*u.mas/u.yr, radial_velocity=bary_corr, distance = 1*u.pc)
        LSR_corr = obs_wrt_bary.transform_to(LSRK()).radial_velocity

        return LSR_corr.value


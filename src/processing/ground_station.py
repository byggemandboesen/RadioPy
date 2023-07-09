from dataclasses import dataclass
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
     - az
     - alt
     - ra
     - dec
    use_eq_coords       Use equatorial coordinates of antenna position (ra, dec)
    LO_freq             Frequency of local oscillator in Hz
    '''
    az: float
    alt: float
    ra: float
    dec: float
    use_eq_coords: bool
    LO_freq: float
    

    def getHorizontalCoordinates(self, GS):
        '''
        Return horizontal coordinates of antenna direction.

        Takes the respective ground station as argument (instance of GroundStation)

        Returns [az, alt]
        '''
        if not self.use_eq_coords:
            return [self.az, self.alt]
        
        # Defines GS QTH
        altaz = AltAz(obstime = GS.TIME, location = GS.QTH, pressure = 0*u.bar)
        # Defines sky-coordinate in equatorial coords
        eq_coord = ICRS(ra=self.ra*u.degree, dec=self.dec*u.degree)
        # Convert
        horizontal_coord = eq_coord.transform_to(altaz)

        return [round(horizontal_coord.az.degree, 3), round(horizontal_coord.alt.degree, 3)]
        

    def getEquatorialCoordinates(self, GS):
        '''
        Return equatorial coordinates of antenna direction.

        Takes the respective ground station as argument (instance of GroundStation)

        Returns [ra, dec]
        '''
        if self.use_eq_coords:
            return [self.ra, self.dec]
        
        # Define horizontal coordinates
        horizontal_coord = AltAz(alt = self.alt*u.degree, az = self.az*u.degree, pressure = 0*u.bar, obstime = GS.TIME,location=GS.QTH)
        # Convert
        eq_coord = SkyCoord(horizontal_coord.transform_to(ICRS()))

        return [round(eq_coord.ra.degree, 3), round(eq_coord.dec.degree, 3)]
    

    def getGalacticCoordinates(self, GS):
        '''
        Return galactic coordinates of antenna direction.

        Takes the respective ground station as argument (instance of GroundStation)

        Returns [lon (l), lat (b)]
        '''
        # Define local horizontal coordinate
        az_alt = self.getHorizontalCoordinates(GS)
        horizontal_coord = AltAz(alt = az_alt[1]*u.degree, az = az_alt[0]*u.degree, pressure = 0*u.bar, obstime = GS.TIME,location=GS.QTH)
        # Convert
        gal_coord = horizontal_coord.transform_to(Galactic())

        return [round(gal_coord.l.degree, 3), round(gal_coord.b.degree, 3)]


class GroundStation:
    def __init__(self, lat: float, lon: float, elev: float, time, lsr_correct: bool, antenna: Antenna):
        self.QTH = EarthLocation(lat = lat*u.degree, lon=lon*u.degree,height=elev*u.m)
        self.TIME = Time(time)
        self.lsr_correct = lsr_correct

    
    def freqToVel(self, rest_freq, freq):
        '''
        Compute radial velocity from frequency

        OBS!! Note the negative sign on the radial velocity due to astropy calculating doppler
        '''
        spectral_freq = u.doppler_radio(rest_freq*u.Hz)
        measured = freq*u.Hz
        radial_vel = -measured.to(u.km/u.s,equivalencies=spectral_freq)

        return radial_vel.value


    def velToFreq(self, rest_freq, radial_vel):
        '''
        Compute frequency from radial velocity

        OBS!! Note the negative sign on the radial velocity due to astropy calculating doppler
        '''
        spectral_freq = u.doppler_radio(rest_freq*u.Hz)
        measured = -radial_vel*u.km/u.s
        freq = measured.to(u.Hz,equivalencies=spectral_freq)

        return freq.value


    def getLSRCorrection(self, ra, dec):
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

        return round(LSR_corr.value, 3)


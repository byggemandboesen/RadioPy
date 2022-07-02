from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, LSRK, EarthLocation, AltAz, ICRS, Galactic

# Suppress warnings
import warnings
from astropy.utils.exceptions import AstropyWarning
warnings.simplefilter('ignore', category=AstropyWarning)


class Ephemeris():    
    def __init__(self, lat, lon, elev, time):
        self.QTH = EarthLocation(lat = lat*u.degree, lon=lon*u.degree,height=elev*u.m)
        self.TIME = Time(time)

    def lineToFreq(self, line):
        '''
        Get the frequency from a given spectral line
        '''
        spectral_lines = {
            "H1": 1420405752,
            "OH_1612": 1612231000,
            "OH_1665": 1665402000,
            "OH_1667": 1667359000,
            "OH_1720": 1720530000,
        }

        if line not in spectral_lines.keys():
            print("Invalid line name. Please check the README for all spectral line names")
            quit()
        else:
            return int(spectral_lines[line])
        
    def galactic(self, alt, az):
        '''
        Compute galactic coordinates from azimuth and altitude
        '''
        horizontal_coord = AltAz(alt = alt*u.degree, az = az*u.degree, pressure = 0*u.bar, obstime = self.TIME,location=self.QTH)
        gal_coord = horizontal_coord.transform_to(Galactic())

        # Return lon (l), lat (b)
        return round(gal_coord.l.degree, 4), round(gal_coord.b.degree, 4)
    
    def equatorial(self, alt, az):
        '''
        Compute equatorial coordinates from azimuth and altitude
        '''
        horizontal_coord = AltAz(alt = alt*u.degree, az = az*u.degree, pressure = 0*u.bar, obstime = self.TIME,location=self.QTH)
        eq_coord = SkyCoord(horizontal_coord.transform_to(ICRS()))

        return round(eq_coord.ra.degree, 4), round(eq_coord.dec.degree, 4)
    
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
        sky_coord = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame="icrs")
        # Correction wrt. barycenter
        bary_corr = sky_coord.radial_velocity_correction(obstime = self.TIME, location = self.QTH)
        # Transform to km/s
        bary_corr = bary_corr.to(u.km/u.s)
        # Finally, correction wrt. LSR
        obs_wrt_bary = ICRS(ra=ra*u.deg, dec=dec*u.degree, pm_ra_cosdec=0*u.mas/u.yr, pm_dec=0*u.mas/u.yr, radial_velocity=bary_corr, distance = 1*u.pc)
        LSR_corr = obs_wrt_bary.transform_to(LSRK()).radial_velocity

        return LSR_corr.value


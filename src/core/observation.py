from __future__ import annotations
import numpy as np


class Observation:
    '''
    Write, read or manipulate observation files
    '''
    def __init__(self, path: str, obs_time: str = "", local_coord: np.ndarray = np.zeros(2),
                eq_coord: np.ndarray = np.zeros(2), gal_coord: np.ndarray = np.zeros(2),
                lsr_corr: float = 0.0, freqs: np.ndarray = np.zeros(1024),
                radial_vel: np.ndarray = np.zeros(1024), data: np.ndarray = np.zeros(1024)) -> None:
        
        self.PATH = path
        self.OBS_TIME = obs_time
        self.LOCAL_COORD = local_coord
        self.EQ_COORD = eq_coord
        self.GAL_COORD = gal_coord
        self.LSR_CORR = lsr_corr
        self.FREQS = freqs
        self.RADIAL_VEL = radial_vel
        self.DATA = data

    def __sub__(self, other: Observation) -> Observation:
        '''
        Subtract observation data from each other

        If doing x-y, then subtract y-data from x, and keep info from x.
        '''
        other_data = other.readObservationFile()
        self.DATA -= other_data["data"]

    
    def writeObservationFile(self) -> None:
        '''
        Write observation file from data

        obs_data        -   List of all the observation info (time, coords etc)
        data            -   Numpy array of observation data
        obs_freqs       -   Numpy array of observation frequencies
        radial_vel      -   Numpy array of radial velocities
        '''
        obs_data = [
            f"Observation time: {self.OBS_TIME}\n",
            f"Local coordinates: {self.LOCAL_COORD[0]},{self.LOCAL_COORD[1]}\n",
            f"Equatorial coordinates: {self.EQ_COORD[0]},{self.EQ_COORD[1]}\n",
            f"Galactic coordinates: {self.GAL_COORD[0]},{self.GAL_COORD[1]}\n",
            f"LSR correction: {self.LSR_CORR}\n",
            "Data,Observer frequency,Radial velocity\n"
        ]
        with open(self.PATH, "w") as obs_file:
            obs_file.writelines(obs_data)

            for i in range(len(self.DATA)):
                obs_file.write(f"{self.DATA[i]},{self.FREQS[i]},{self.RADIAL_VEL[i]}\n")
        obs_file.close()


    def readObservationFile(self) -> dict:
        '''
        Read observation file as dictionary with the following (k,v) pairs

        obs_time        - Time of observation (UTC)                     string
        obs_coord_azel  - Horizontal coordinates of observation         np.ndarray, float
        obs_coord_eq    - Equatorial coordinates of observation         np.ndarray, float
        obs_coord_gal   - Galactic coordinates of observation           np.ndarray, float
        lsr_cor         - LSR correction for observation                float
        data            - Data for observation                          np.ndarray, float
        freq            - Observer frequency for observation            np.ndarray, float
        radial_vel      - Radial velocity of observation                np.ndarray, float
        '''

        txt_file = open(self.PATH, 'r').readlines()
        obs_time = str(txt_file[0][18:-1]) # Strip newline char
        obs_coord_azel = np.array(txt_file[1].split(": ")[1].split(","), dtype=float)
        obs_coord_eq = np.array(txt_file[2].split(": ")[1].split(","), dtype=float)
        obs_coord_gal = np.array(txt_file[3].split(": ")[1].split(","), dtype=float)
        lsr_cor = float(txt_file[4].split(": ")[1])

        data_mat = np.array([line.split(",") for line in txt_file[6:]])
        data = np.array(data_mat[:,0], dtype=float)
        freq = np.array(data_mat[:,1], dtype=float)
        radial_vel = np.array([val.strip("\n") for val in data_mat[:,2]], dtype=float)

        obs_dict = {
            "obs_time": obs_time,
            "obs_coord_azel": obs_coord_azel,
            "obs_coord_eq": obs_coord_eq,
            "obs_coord_gal": obs_coord_gal,
            "lsr_cor": lsr_cor,
            "data": data,
            "freq": freq,
            "radial_vel": radial_vel
        }
        
        return obs_dict


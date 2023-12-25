import numpy as np


class Observation:
    '''
    Write, read or manipulate observation files
    '''
    def __init__(self, path: str) -> None:
        self.PATH = path

    
    def writeObservationFile(self, obs_data: list, data: np.ndarray, obs_freqs: np.ndarray, radial_vel: np.ndarray) -> None:
        '''
        Write observation file from data

        obs_data        -   List of all the observation info (time, coords etc)
        data            -   Numpy array of observation data
        obs_freqs       -   Numpy array of observation frequencies
        radial_vel      -   Numpy array of radial velocities
        '''

        with open(self.PATH, "w") as obs_file:
            obs_file.writelines(obs_data)

            for i in range(len(data)):
                obs_file.write(f"{data[i]},{obs_freqs[i]},{radial_vel[i]}\n")
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


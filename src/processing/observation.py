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




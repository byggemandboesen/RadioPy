import configparser
import dearpygui.dearpygui as dpg


# Default parameters
DEFAULT_PARAM = {
    "lat": 0,
    "lon": 0,
    "elev": 20,
    "lsr_correct": True,
    "az": 0,
    "alt": 0,
    "ra": 0,
    "dec": 0,
    "use_eq_coords": False,
    "lo_freq": 0,
    "driver": "none",
    "sample_rate": 0,
    "ppm_offset": 0,
    "bins": 4096,
    "fft_num": 1000,
    "median": 0,
    "dc_offset": False,
    "spectral_line": "Neutral hydrogen, 1420MHz",
    "y_min": 0.0,
    "y_max": 0.0,
    "save_data": False
}

# Available spectral lines
SPECTRAL_LINES = {
    "Neutral hydrogen, 1420MHz": "H1_1420",
    "Hydroxyl, 1612MHz": "OH_1612",
    "Hydroxyl, 1665MHz": "OH_1665",
    "Hydroxyl, 1667MHz": "OH_1667",
    "Hydroxyl, 1720MHz": "OH_1720"
}


def loadConfigError():
    print("Error loading config file...")
    print("Avoid deleting/moving the file from its original directory")


def loadConfig():
    '''
    Loads parameters from config file
    Returns config object
    '''
    print("Loading config file...")
    conf_obj = configparser.ConfigParser(comment_prefixes='#', allow_no_value=True)
    res = conf_obj.read("config.ini")
    if not res:
        loadConfigError()
        quit()
    return conf_obj


def applyDefaultParameters():
    '''
    Applies default settings to all parameters
    '''
    print("Applying default parameters...")

    dpg.set_value("lat", DEFAULT_PARAM["lat"])
    dpg.set_value("lon", DEFAULT_PARAM["lon"])
    dpg.set_value("elev", DEFAULT_PARAM["elev"])
    dpg.set_value("lsr_correct", DEFAULT_PARAM["lsr_correct"])
    dpg.set_value("az", DEFAULT_PARAM["az"])
    dpg.set_value("alt", DEFAULT_PARAM["alt"])
    dpg.set_value("ra", DEFAULT_PARAM["ra"])
    dpg.set_value("dec", DEFAULT_PARAM["dec"])
    dpg.set_value("use_eq_coords", DEFAULT_PARAM["use_eq_coords"])
    dpg.set_value("lo_freq", DEFAULT_PARAM["lo_freq"])

    dpg.set_value("driver", DEFAULT_PARAM["driver"])
    dpg.set_value("sample_rate", DEFAULT_PARAM["sample_rate"])
    dpg.set_value("ppm_offset", DEFAULT_PARAM["ppm_offset"])
    dpg.set_value("bins", DEFAULT_PARAM["bins"])

    dpg.set_value("fft_num", DEFAULT_PARAM["fft_num"])
    dpg.set_value("median", DEFAULT_PARAM["median"])
    dpg.set_value("dc_offset", DEFAULT_PARAM["dc_offset"])
    dpg.set_value("spectral_line", DEFAULT_PARAM["spectral_line"])
    dpg.set_value("y_min", DEFAULT_PARAM["y_min"])
    dpg.set_value("y_max", DEFAULT_PARAM["y_max"])
    dpg.set_value("save_data", DEFAULT_PARAM["save_data"])


def updateParameters():
    '''
    Loads parameters from config file and updates UI
    '''
    print("Applying parameters from config...")
    config = loadConfig()
    
    # Not very beautiful, but gets the job done...
    dpg.set_value("lat", config.getfloat("Ground station", "lat"))
    dpg.set_value("lon", config.getfloat("Ground station", "lon"))
    dpg.set_value("elev", config.getfloat("Ground station", "elev"))
    dpg.set_value("lsr_correct", config.getboolean("Ground station", "lsr_correct"))
    dpg.set_value("az", config.getfloat("Ground station", "az"))
    dpg.set_value("alt", config.getfloat("Ground station", "alt"))
    dpg.set_value("ra", config.getfloat("Ground station", "ra"))
    dpg.set_value("dec", config.getfloat("Ground station", "dec"))
    dpg.set_value("use_eq_coords", config.getboolean("Ground station", "use_eq_coords"))
    dpg.set_value("lo_freq", config.getint("Ground station", "lo_freq"))

    dpg.set_value("driver", config.get("SDR", "driver"))
    dpg.set_value("sample_rate", config.getint("SDR", "sample_rate"))
    dpg.set_value("ppm_offset", config.getint("SDR", "ppm_offset"))
    dpg.set_value("bins", config.getint("SDR", "bins"))

    dpg.set_value("fft_num", config.getint("Spectral line", "fft_num"))
    dpg.set_value("median", config.getint("Spectral line", "median"))
    dpg.set_value("dc_offset", config.getboolean("Spectral line", "dc_offset"))
    dpg.set_value("spectral_line", config.get("Spectral line", "spectral_line"))

    dpg.set_value("y_min", config.getfloat("Spectral line", "y_min"))
    dpg.set_value("y_max", config.getfloat("Spectral line", "y_max"))
    dpg.set_value("save_data", config.getboolean("Spectral line", "save_data"))


def applyParameters():
    '''
    Applies current parameters to config file
    '''
    print("Applying parameters to config...")
    config = loadConfig()
    
    # Not very beautiful, but gets the job done...
    config.set("Ground station", "lat", str(round(dpg.get_value("lat"), 3)))
    config.set("Ground station", "lon", str(round(dpg.get_value("lon"), 3)))
    config.set("Ground station", "elev", str(round(dpg.get_value("elev"), 3)))
    config.set("Ground station", "lsr_correct", str(dpg.get_value("lsr_correct")))
    config.set("Ground station", "az", str(round(dpg.get_value("az"), 3)))
    config.set("Ground station", "alt", str(round(dpg.get_value("alt"), 3)))
    config.set("Ground station", "ra", str(round(dpg.get_value("ra"), 3)))
    config.set("Ground station", "dec", str(round(dpg.get_value("dec"), 3)))
    config.set("Ground station", "use_eq_coords", str(dpg.get_value("use_eq_coords")))
    config.set("Ground station", "lo_freq", str(dpg.get_value("lo_freq")))

    config.set("SDR", "driver", str(dpg.get_value("driver")))
    config.set("SDR", "sample_rate", str(dpg.get_value("sample_rate")) if str(dpg.get_value("sample_rate")) != "" else 0)
    config.set("SDR", "ppm_offset", str(dpg.get_value("ppm_offset")))
    config.set("SDR", "bins", str(dpg.get_value("bins")))

    config.set("Spectral line", "fft_num", str(dpg.get_value("fft_num")))
    config.set("Spectral line", "median", str(dpg.get_value("median")))
    config.set("Spectral line", "dc_offset", str(dpg.get_value("dc_offset")))
    config.set("Spectral line", "spectral_line", SPECTRAL_LINES[str(dpg.get_value("spectral_line"))])
    config.set("Spectral line", "y_min", str(round(dpg.get_value("y_min"), 3)))
    config.set("Spectral line", "y_max", str(round(dpg.get_value("y_max"), 3)))
    config.set("Spectral line", "save_data", str(dpg.get_value("save_data")))

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

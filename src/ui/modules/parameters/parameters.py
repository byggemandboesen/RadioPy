import sys, json, soapy
import dearpygui.dearpygui as dpg

# Callbaks for module
import ui.modules.parameters.callbacks as callbacks
# Soapy device for drivers, sample rates and etc
from soapy import SDR

DEFAULT_CONFIG = {
    "observer": {
        "lat": 0.0,
        "lon": 0.0,
        "elev": 20,
        "az": 0.0,
        "alt": 0.0
    },
    "obj": {
        "pulsar": False,
        "spectral_line": "H1",
        "LSR_correct": True
    },
    "sdr": {
        "driver": "rtlsdr",
        "sample_rate": 3200000,
        "PPM_offset": 0,
        "bins": 4096,
        "fft_num": 1000,
        "median": 0,
        "dc_offset": False
    },
    "frontend": {
        "LO": 0
    },
    "data": {
        "plot_limits": [0.0,0.0],
        "write_data": False,
        "type": "csv"
    }
}


def parametersModule():
    '''
    Module containing software parameters - eg. everything in config.json
    '''

    with dpg.collapsing_header(label = "Parameters"):
        dpg.add_text("Modify observing parameters")

        # Observer node
        with dpg.tree_node(label = "Observer"):
            dpg.add_text("Observer location")
            with dpg.group(horizontal=True):
                dpg.add_input_float(label = "Lat", width = 150, tag = "lat")
                dpg.add_input_float(label = "Lon", width = 150, tag = "lon")
            
            dpg.add_text("Sky coordinates")
            with dpg.group(horizontal=True):
                dpg.add_input_float(label = "Az", width = 150, tag = "az")
                dpg.add_input_float(label = "Alt", width = 150, tag = "alt")

            dpg.add_input_float(label = "Elevation", tag = "elev")

        # Object node #TODO - Revise this part
        with dpg.tree_node(label = "Object"):
            dpg.add_text("Object type/information")
        
        
        # SDR node
        with dpg.tree_node(label = "SDR"):
            dpg.add_text("SDR parameters")
            
            # Determine available soapy devices
            available_drives = soapy.listDrivers()
            dpg.add_combo(available_drives, label = "Driver", tag="driver", width = -150, callback=selectedSDR)
            # SDR sample rates
            dpg.add_combo([], label = "Sample rate (MHz)", tag = "sample_rate", width = -150)
            dpg.add_input_int(label = "PPM offset", default_value = 0, tag = "PPM_offset", width = -150)


def selectedSDR():
    '''
    Gets the selected SDR from dropdown menu.
    Proceeds to update sample rate dropdown with specific SDR sample rates
    '''
    driver = dpg.get_value("driver")
    sdr = SDR(driver)
    sample_rates = sdr.getAvailableSampleRates()
    dpg.configure_item("sample_rate", items = sample_rates)


def updateValues():
    print("Updating fields")

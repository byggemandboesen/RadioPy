import dearpygui.dearpygui as dpg

# Handle devices
import soapy
from soapy import SDR

# Update spectral line observation time estimate
from ui.spectral_line.spectral_line_ui import updateTimeEstimate
import ui.callbacks as cb


def parametersWindow(pos: list = [10, 10], w: int = 400, h: int = 500):
    with dpg.window(label= "General parameters", width=w, height=h, no_close=True, pos = pos):
        
        # Ground station
        with dpg.collapsing_header(label = "Ground station"):
            
            dpg.add_text("Geographic location")
            with dpg.group(horizontal=True):
                dpg.add_input_float(label = "Lat", width = 150, tag = "lat", min_value=-90, max_value=90)
                dpg.add_input_float(label = "Lon", width = 150, tag = "lon", max_value=-180, min_value=180)
            dpg.add_input_float(label = "Elevation", tag = "elev", width = -150, default_value=20)

            
            dpg.add_spacer(height=5)
            dpg.add_text("Sky coordinates")
            with dpg.group(horizontal=True):
                dpg.add_input_float(label = "Az", width = 150, tag = "az", min_value=0, max_value=360)
                dpg.add_input_float(label = "Alt", width = 150, tag = "alt", min_value=0, max_value=90)

            with dpg.group(horizontal=True):
                dpg.add_input_float(label = "RA", width = 150, tag = "ra", min_value=0, max_value=360)
                dpg.add_input_float(label = "Dec", width = 150, tag = "dec", min_value=-90, max_value=90)
            dpg.add_checkbox(label = "Use equatorial coordinates", tag="use_eq_coords", default_value=False)
            
        
        # SDR section
        with dpg.collapsing_header(label = "SDR/frontend"):
            dpg.add_text("SDR")
            # Determine available soapy devices
            available_drives = soapy.listDrivers()
            dpg.add_combo(available_drives, default_value="none" , label = "Driver", tag="driver", width = -150, callback=selectedSDR)
            
            # SDR sample rates are added once device is selected
            dpg.add_combo([], label = "Sample rate (MHz)", tag = "sample_rate", width = -150 , callback=updateTimeEstimate)
            dpg.add_input_int(label = "PPM offset", default_value = 0, tag = "ppm_offset", width = -150)

            dpg.add_spacer(height=5)
            dpg.add_text("Downconverter")
            dpg.add_input_int(label = "LO frequency", default_value=0, width=-150, tag = "lo_freq")
        
        dpg.add_spacer(height=5)
        dpg.add_button(label = "Load config parameters", callback=cb.updateParameters)
        dpg.add_button(label = "Apply defult parameters", callback=cb.applyDefaultParameters)
        # dpg.add_button(label = "Apply parameters to config", callback=cb.applyParameters)


def selectedSDR():
    '''
    Gets the selected SDR from dropdown menu.
    Proceeds to update sample rate dropdown with specific SDR sample rates
    '''
    driver = dpg.get_value("driver")
    sdr = SDR(driver)
    sample_rates = sdr.getAvailableSampleRates()
    dpg.configure_item("sample_rate", items = sample_rates)
import dearpygui.dearpygui as dpg

# Handle devices
import processing.soapy as soapy
from processing.soapy import SDR

# Update spectral line observation time estimate
from ui.tabs.spectral_line_ui import updateTimeEstimate
import ui.config_callbacks as cb


def parametersTab():
    with dpg.tab(label= "General parameters"):
        
        # Ground station
        with dpg.collapsing_header(label = "Ground station", default_open=True):
            
            dpg.add_text("Geographic location")
            with dpg.group(horizontal=True):
                dpg.add_input_float(label = "Lat", width = 150, tag = "lat", min_value=-90, max_value=90)
                dpg.add_input_float(label = "Lon", width = 150, tag = "lon", max_value=-180, min_value=180)
            dpg.add_input_float(label = "Elevation", tag = "elev", width = 150, default_value=20)

            
            dpg.add_spacer(height=5)
            dpg.add_text("Sky coordinates")
            with dpg.group(horizontal=True):
                dpg.add_input_float(label = "Az", width = 150, tag = "az", min_value=0, max_value=360)
                dpg.add_input_float(label = "Alt", width = 150, tag = "alt", min_value=0, max_value=90)

            with dpg.group(horizontal=True):
                dpg.add_input_float(label = "RA", width = 150, tag = "ra", min_value=0, max_value=360)
                dpg.add_input_float(label = "Dec", width = 150, tag = "dec", min_value=-90, max_value=90)
            dpg.add_checkbox(label = "Use equatorial coordinates", tag="use_eq_coords", default_value=False)
            
        
        dpg.add_spacer(height=7.5)
        # SDR section
        with dpg.collapsing_header(label = "SDR/frontend", default_open=True):
            dpg.add_text("SDR")

            dpg.add_button(label = "Refresh", width = 100, callback=updateDrivers)
            dpg.bind_item_theme(dpg.last_item(), "button_theme")

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
        dpg.add_button(label = "Apply parameters to config", callback=cb.applyParameters)


def updateDrivers():
    '''
    Updates the driver dropdown with discovered drivers.
    Proceeds to also refresh sample rates if device is already chosen.
    '''
    current_driver = dpg.get_value("driver")
    available_drivers = soapy.listDrivers()
    dpg.configure_item("driver", items = available_drivers)
    if current_driver != "none" and current_driver in available_drivers:
        selectedSDR()
    else:
        dpg.set_value("driver", "none")
        dpg.configure_item(item = "sample_rate", items = [])
        dpg.set_value("sample_rate", 0)


def selectedSDR():
    '''
    Gets the selected SDR from dropdown menu.
    Proceeds to update sample rate dropdown with specific SDR sample rates
    '''
    driver = dpg.get_value("driver")
    sdr = SDR(driver)
    sample_rates = sdr.getAvailableSampleRates()
    dpg.set_value("sample_rate", sample_rates[0])
    dpg.configure_item("sample_rate", items = sample_rates)
    del sdr
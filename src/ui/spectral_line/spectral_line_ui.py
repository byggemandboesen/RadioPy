import os
import dearpygui.dearpygui as dpg

import ui.callbacks as CB


def spectralLineWindow(pos: list = [420,10], w: int = 400, h: int = 500):
    with dpg.window(label= "Spectral line", width=w, height=h, no_close=True, pos=pos):
        
        with dpg.collapsing_header(label = "Data collection"):
            dpg.add_input_int(label = "Bins", default_value=4096, tag = "bins", width = -150, callback = updateTimeEstimate)
            dpg.add_input_int(label = "FFT average", default_value=1000, tag = "fft_num", width = -150, callback = updateTimeEstimate)
            dpg.add_input_int(label = "Median", default_value=0, tag = "median", width = -150, callback = updateTimeEstimate)
            
            with dpg.group(horizontal=True):
                dpg.add_checkbox(label = "DC offset", default_value=False, tag = "dc_offset")
                dpg.add_text("(?)", color=(0,0,255,255), tag = "dc_offset_tooltip")
            with dpg.tooltip("dc_offset_tooltip"):
                dpg.add_text("Offset center frequency to avoid DC spike overlap")


        with dpg.collapsing_header(label = "Object"):
            dpg.add_text("Select spectral line")
            dpg.add_combo(list(CB.SPECTRAL_LINES.keys()), default_value=list(CB.SPECTRAL_LINES.keys())[0], tag = "spectral_line")
            
            with dpg.group(horizontal=True):
                dpg.add_checkbox(label = "Correct for LSR", tag="lsr_correct", default_value=True)
                dpg.add_text("(?)", color=(0,0,255,255), tag = "lsr_tooltip")

            with dpg.tooltip("lsr_tooltip"):
                dpg.add_text("Correct radial velocity to the local standard of rest")
        
        with dpg.collapsing_header(label = "Data visualization/saving"):
            with dpg.group(horizontal=True):
                dpg.add_text("Plot limits")
                dpg.add_text("(?)", color=(0,0,255,255), tag = "plot_limits_tooltip")

            with dpg.group(horizontal=True):
                dpg.add_input_float(label="Y min", width = 150, default_value=0, tag="y_min")
                dpg.add_input_float(label="Y max", width = 150, default_value=0, tag="y_max")
            
            with dpg.tooltip("plot_limits_tooltip"):
                dpg.add_text("Y-axis plot limits. If left to 0,0 axis will be autoscaled")
            

            dpg.add_checkbox(label = "Save data", default_value=False, tag="save_data")


        # Run observation section
        dpg.add_spacer(height=10)
        with dpg.theme(tag = "run_spectral_button_theme"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (15, 86, 136,255))
        dpg.add_button(label = "Run observation", callback=beginObservation)
        dpg.bind_item_theme(dpg.last_item(), "run_spectral_button_theme")
        with dpg.group(horizontal=True):
            dpg.add_text("Estimated observation time: ")
            dpg.add_text("NaN", tag = "estimated_time")
            dpg.add_text("seconds")


def updateTimeEstimate():
    '''
    Update estimated observation duration
    '''
    if dpg.get_value("sample_rate") == "none":
        return
    
    sample_rate = float(dpg.get_value("sample_rate"))
    bins = float(dpg.get_value("bins"))
    ffts = float(dpg.get_value("fft_num"))

    time_estimate = round(bins*ffts/sample_rate, 2)
    dpg.set_value("estimated_time", time_estimate)


def beginObservation():
    '''
    Starts an observation in another process
    '''
    CB.applyParameters()
    os.system('py radiopy.py -s' if os.name =='nt' else 'python3 radiopy.py -s')
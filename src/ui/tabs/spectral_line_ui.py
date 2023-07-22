import os
import dearpygui.dearpygui as dpg

import ui.config_callbacks as CB
import ui.ui_constants as UI_CONSTS

def spectralLineTab():
    with dpg.tab(label= "Spectral line"):
        
        with dpg.collapsing_header(label = "Data collection", default_open=True):
            dpg.add_text("Configure data collection parameters")
            dpg.add_input_int(label = "Bins", default_value=1024, tag = "bins", width = UI_CONSTS.W_NUM_INP_SING_COL, callback = updateTimeEstimate)
            dpg.add_input_int(label = "FFT average", default_value=1000, tag = "fft_num", width = UI_CONSTS.W_NUM_INP_SING_COL, callback = updateTimeEstimate)
            dpg.add_input_int(label = "Smoothing", default_value=0, tag = "smoothing", width = UI_CONSTS.W_NUM_INP_SING_COL, callback = updateTimeEstimate)
            
            # with dpg.group(horizontal=True):
            #     dpg.add_checkbox(label = "DC offset", default_value=False, tag = "dc_offset")
            #     dpg.add_text("(?)", color=(0,0,255,255), tag = "dc_offset_tooltip")
            # with dpg.tooltip("dc_offset_tooltip"):
            #     dpg.add_text("Offset center frequency to avoid DC spike overlap")

            with dpg.group(horizontal=True):
                dpg.add_input_float(label="Redshift", default_value=0, min_value=0, min_clamped=True, max_clamped=True, width=UI_CONSTS.W_NUM_INP_SING_COL, tag="redshift")
                dpg.add_text("(?)", color=(0,0,255,255), tag = "redshift_tooltip")

            with dpg.tooltip("redshift_tooltip"):
                dpg.add_text("Account for target redshift")
            
            with dpg.group(horizontal=True):
                dpg.add_checkbox(label = "Correct for LSR", tag="lsr_correct", default_value=True)
                dpg.add_text("(?)", color=(0,0,255,255), tag = "lsr_tooltip")

            with dpg.tooltip("lsr_tooltip"):
                dpg.add_text("Correct radial velocity to the local standard of rest")
            
        # dpg.add_spacer(height=UI_CONSTS.H_COLL_HEAD_SPACER)
        # with dpg.collapsing_header(label = "Object", default_open=True):
        #     dpg.add_text("Select spectral line")
        #     dpg.add_combo(list(CB.SPECTRAL_LINES.keys()), default_value=list(CB.SPECTRAL_LINES.keys())[0], tag = "spectral_line")
            
        dpg.add_spacer(height=UI_CONSTS.H_COLL_HEAD_SPACER)
        with dpg.collapsing_header(label = "Data visualization/saving", default_open=True):
            with dpg.group(horizontal=True):
                dpg.add_text("Plot limits")
                dpg.add_text("(?)", color=(0,0,255,255), tag = "plot_limits_tooltip")

            with dpg.group(horizontal=True):
                dpg.add_input_float(label="Y min", width = UI_CONSTS.W_NUM_INP_DOUB_COL, default_value=0, tag="y_min")
                dpg.add_input_float(label="Y max", width = UI_CONSTS.W_NUM_INP_DOUB_COL, default_value=0, tag="y_max")
            
            with dpg.tooltip("plot_limits_tooltip"):
                dpg.add_text("Y-axis plot limits. If left to 0,0 axis will be autoscaled")
            

            dpg.add_checkbox(label = "Save data", default_value=True, tag="save_data")


        # Run observation section
        dpg.add_spacer(height=10)
        dpg.add_button(label = "Run observation", callback=beginObservation)
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
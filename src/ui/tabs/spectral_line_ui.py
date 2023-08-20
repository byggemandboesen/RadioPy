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
                dpg.add_input_float(label="Rest freq (MHz)", default_value=0, min_value=0, min_clamped=True, width=UI_CONSTS.W_NUM_INP_SING_COL, tag="restfreq")
                dpg.add_text("(?)", color=(0,0,255,255), tag = "restfreq_tooltip")

            with dpg.tooltip("restfreq_tooltip"):
                dpg.add_text("Rest frequency to determine radial velocites from.\nIf left at 0, default will be SDR center frequency")
            
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
                dpg.add_input_float(label="MIN", width = UI_CONSTS.W_NUM_INP_DOUB_COL, default_value=0, tag="y_min", format="%.7f")
                dpg.add_input_float(label="MAX", width = UI_CONSTS.W_NUM_INP_DOUB_COL, default_value=0, tag="y_max", format="%.7f")
            
            with dpg.tooltip("plot_limits_tooltip"):
                dpg.add_text("Y-axis plot limits. If left to 0,0 axis will be autoscaled")

            # dpg.add_text("Second x-axis:")
            # dpg.add_combo(["Velocity", "Rest-frequency"], default_value="Velocity", tag="secax", width=UI_CONSTS.W_NUM_INP_SING_COL)

            dpg.add_checkbox(label = "Save data", default_value=True, tag="save_data")


        dpg.add_spacer(height=UI_CONSTS.H_COLL_HEAD_SPACER)
        with dpg.collapsing_header(label = "Calibration", default_open=True):
            with dpg.group(horizontal=True):
                dpg.add_text("Calibrate bandpass of observation ")
                dpg.add_text("(?)", color=(0,0,255,255), tag = "calibration_tooltip")
            with dpg.tooltip("calibration_tooltip"):
                dpg.add_text("Calibrate observation from reference observation (cold sky for example)")
            
            
            dpg.add_text("Load primary observation file")
            with dpg.group(horizontal=True):
                dpg.add_input_text(hint = "Main file path", width = UI_CONSTS.W_TXT_INP, tag = "main_path", callback=updateDataViewer)
                dpg.add_button(label = "Browse", callback=lambda: dpg.show_item("main_file_dialog"))
            
            dpg.add_text("Load calibration file")
            with dpg.group(horizontal=True):
                dpg.add_input_text(hint = "Calibration file", width = UI_CONSTS.W_TXT_INP, tag = "calibration_path", callback=updateDataViewer)
                dpg.add_button(label = "Browse", callback=lambda: dpg.show_item("cal_file_dialog"))
            
            # File dialog
            with dpg.file_dialog(label = "Browse", show = False, tag = "main_file_dialog", width=600, height=400, default_path=os.getcwd(), callback=fileDialogCallBack, cancel_callback=fileDialogCancelledCallBack, user_data="main"): # TODO - Update callback
                dpg.add_file_extension(".csv", color=(0, 255, 0, 255))
            with dpg.file_dialog(label = "Browse", show = False, tag = "cal_file_dialog", width=600, height=400, default_path=os.getcwd(), callback=fileDialogCallBack, cancel_callback=fileDialogCancelledCallBack, user_data="cal"): # TODO - Update callback
                dpg.add_file_extension(".csv", color=(0, 255, 0, 255))

            with dpg.tree_node(label="Configure calibration parameters", default_open=True):
                with dpg.group(horizontal=True):
                    dpg.add_input_float(label="Scaling ", width=UI_CONSTS.W_NUM_INP_SING_COL, default_value=1, tag="calibration_scaling_const")
                    dpg.add_text("(?)", color=(0,0,255,255), tag = "calibration_scaling_tooltip")
                with dpg.tooltip("calibration_scaling_tooltip"):
                    dpg.add_text("Subtract calibration bandpass multiplied by scaling constant from observation data")
                dpg.add_button(label="Autoscale")

                dpg.add_spacer(height=2.5)
                dpg.add_text("Line width and position")
                dpg.add_input_int(label="Line position (bin)", default_value=0, width=UI_CONSTS.W_NUM_INP_SING_COL, tag="line_center")
                dpg.add_input_int(label="Line width (bins)", default_value=200, width=UI_CONSTS.W_NUM_INP_SING_COL, tag="line_width")

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


def fileDialogCallBack(sender: dict, app_data: str, user_data: str) -> None:
    '''
    Callback for calibration file dialog
    '''
    path = app_data["file_path_name"]
    if user_data == "main":
        dpg.set_value("main_path", path)
    else:
        dpg.set_value("calibration_path", path)

def fileDialogCancelledCallBack() -> None:
    '''
    Callback for cancelled file browsing
    '''
    return


def updateDataViewer() -> None:
    '''
    Update data viewer from the loaded files and calibration
    '''
    return
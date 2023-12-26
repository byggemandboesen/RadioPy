import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np
import os

import ui.ui_constants as UI_CONSTS
from src.core.observation import Observation
import src.core.dsp as DSP
from src.ui.dataviewer import updateLineSeries #, Add Gaussian fit etc...

row_names = [
    "Observation time",
    "Local coordinates",
    "Equatorial coordinates",
    "Galactic coordinates",
    "LSR correction"
]
obs_kw_names = [
    "obs_time",
    "obs_coord_azel",
    "obs_coord_eq",
    "obs_coord_gal",
    "lsr_cor"
]

def analysisTab():
    '''
    Module for analysing data files - Gaussian fitting etc.
    '''
    with dpg.tab(label="Analysis"):
        dpg.add_text("Load file to view and edit data contents")

        dpg.add_spacer(height=UI_CONSTS.H_COLL_HEAD_SPACER)
        with dpg.group(horizontal=True):
            dpg.add_text("Load data")
            dpg.add_spacer(width=100)
            dpg.add_button(label = "Browse", width=UI_CONSTS.W_TXT_INP, callback=lambda: dpg.show_item("analysis_file_dialog"))
            dpg.bind_item_theme(dpg.last_item(), "button_theme")
        # File dialog
        with dpg.file_dialog(label = "Browse", directory_selector=False, show = False, 
                            tag = "analysis_file_dialog", width=600, 
                            height=400, default_path=os.getcwd(), 
                            callback=lambda s, a, u: dpg.set_value("analysis_file_path", UI_CONSTS.fileBrowserCallback(s, a, u)),
                            cancel_callback=UI_CONSTS.fileBrowserCancelled):
            dpg.add_file_extension(".txt", color=(0, 255, 0, 255))

        dpg.add_input_text(hint="Path", width=UI_CONSTS.W_TXT_INP, tag="analysis_file_path", callback=updateObservation)
        dpg.add_button(label="Refresh", callback=updateObservation)
        dpg.bind_item_theme(dpg.last_item(), "button_theme")


        # OBSERVATION INFO
        dpg.add_spacer(height=UI_CONSTS.H_COLL_HEAD_SPACER)
        dpg.add_text("Observation info")
        with dpg.table(tag="observation_table", borders_innerH=True,
                       borders_outerH=True, borders_innerV=True,
                       borders_outerV=True, resizable=True):
            dpg.add_table_column(label = "Parameter")
            dpg.add_table_column(label = "Value")

            for name in row_names:
                with dpg.table_row(tag=name+"_row"):
                    dpg.add_text(name)
                    dpg.add_text("", tag=name+"_value")
        

        dpg.add_spacer(height=UI_CONSTS.H_COLL_HEAD_SPACER)
        # DATA EDITING
        with dpg.collapsing_header(label="Edit", default_open=True):
            dpg.add_text("Edit current observation")
            dpg.add_input_int(label="Smoothing", min_clamped=True, min_value=1, default_value=1, step=1, tag="editing_smoothing", callback=updateObservation)


        dpg.add_spacer(height=UI_CONSTS.H_COLL_HEAD_SPACER)
        # MODEL FITTING
        with dpg.collapsing_header(label="Fitting", default_open=True):
            dpg.add_text("Fit model to data")

        
        dpg.add_spacer(height=UI_CONSTS.H_COLL_HEAD_SPACER)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Plot current data")
            dpg.bind_item_theme(dpg.last_item(), "button_theme")

            dpg.add_checkbox(label="Include fitting", tag="include_fitting")
        
        dpg.add_button(label="Save current data to file", callback=saveToFile)


def updateObservation() -> None:
    '''
    Update observation info fields and spectrum plot
    '''

    file_path = dpg.get_value("analysis_file_path")

    # Some initial checking of the validation of the file
    if not os.path.isfile(file_path):
        # print("Not a valid file path!!")
        return
    try:
        obs = Observation(path=file_path)
        data = obs.readObservationFile()
    except:
        print("Invalid file formatting - not able parse!!")
        return
    
    # Update table with observation information
    for i, k in enumerate(obs_kw_names):
        if type(data[k]) == np.ndarray:
            dat = f"{data[k][0]}, {data[k][1]}"
        else:
            dat = str(data[k])
        dpg.set_value(row_names[i]+"_value", dat)
    
    
    freq, intensity, vel = data["freq"], data["data"], data["radial_vel"]
    intensity = DSP.applySmoothing(intensity, int(dpg.get_value("editing_smoothing")))

    # Finally, update line series
    updateLineSeries(freq, intensity, vel)


def saveToFile() -> None:
    '''
    Save edited data to new file
    '''

    # Get current edited data and write to new observation file
    xdata, ydata, vel = dpg.get_value("spectrum_line_series")[:3]
    obs_time = dpg.get_value(row_names[0]+"_value")
    obs_coord_azel = np.array(dpg.get_value(row_names[1]+"_value").split(", "), dtype=float)
    obs_coord_eq = np.array(dpg.get_value(row_names[2]+"_value").split(", "), dtype=float)
    obs_coord_gal = np.array(dpg.get_value(row_names[3]+"_value").split(", "), dtype=float)
    lsr_cor = float(dpg.get_value(row_names[4]+"_value"))

    # Create observation
    file_name = dpg.get_value("analysis_file_path")[:-4]+"_EDITED.txt"
    new_obs = Observation(path=file_name, obs_time=obs_time, local_coord=obs_coord_azel,
                          eq_coord=obs_coord_eq, gal_coord=obs_coord_gal, lsr_corr=lsr_cor,
                          freqs=xdata, radial_vel=vel, data=ydata)

    new_obs.writeObservationFile()
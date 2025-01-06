import os
import numpy as np
import pandas as pd
import dearpygui.dearpygui as dpg
import matplotlib.pyplot as plt

import ui.ui_constants as UI_CONSTS
from src.core.observation import Observation
import src.core.dsp as DSP
from src.ui.dataviewer import updateLineSeries #, Add Gaussian fit etc...

# from scipy.optimize import curve_fit

row_names = [
    "Observation time",
    "Local coordinates",
    "Equatorial coordinates",
    "Galactic coordinates",
    "LSR correction"
]
obs_kw_names = [
    "time",
    "horizontal_coords",
    "equatorial_coords",
    "galactic_coords",
    "lsr_cor"
]

class AnalysisTab:
    def __init__(self) -> None:
        self.observation = None

        # Continuum/background level
        self.C = None
        # Three lists containing amplitude mean and std for all gaussians
        self.gauss_A = []
        self.gauss_mu = []
        self.gauss_std = []

        with dpg.tab(label="Analysis"):
            with dpg.collapsing_header(label="Observation", default_open=True):
                dpg.add_spacer(height=UI_CONSTS.H_COLL_HEAD_SPACER)
                with dpg.group(horizontal=True):
                    dpg.add_text("Observation directory")
                    dpg.add_spacer(width=5)
                    dpg.add_button(label = "Browse", width=UI_CONSTS.W_TXT_INP, callback=lambda: dpg.show_item("analysis_file_dialog"))
                    dpg.bind_item_theme(dpg.last_item(), "button_theme")
                # File dialog
                with dpg.file_dialog(label = "Browse", directory_selector=True, show = False, 
                                    tag = "analysis_file_dialog", width=600, 
                                    height=400, default_path=os.getcwd(), 
                                    callback=lambda s, a, u: dpg.set_value("observation_directory", UI_CONSTS.fileBrowserCallback(s, a, u)),
                                    cancel_callback=UI_CONSTS.fileBrowserCancelled):
                    pass

                dpg.add_input_text(hint="Directory", width=UI_CONSTS.W_TXT_INP, tag="observation_directory", callback=self.updateObservation)
                dpg.add_button(label="Refresh", callback=self.updateObservation)
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
            

            # MODEL FITTING
            dpg.add_spacer(height=UI_CONSTS.H_COLL_HEAD_SPACER)
            with dpg.collapsing_header(label="Fitting", default_open=True):
                dpg.add_text("Fit model to data")
                dpg.add_checkbox(label="Toggle model", tag="include_fitting")

                dpg.add_input_float(label="Continuum level", tag="continuum_level", width=UI_CONSTS.W_NUM_INP_SING_COL)
                dpg.add_text("Modify Gaussian profiles")
                dpg.add_combo(items=[f"Gaussian {i+1}" for i in range(len(self.gauss_A))], tag="gaussian_dropdown", width=UI_CONSTS.W_TXT_INP, callback=self.updateSelectedGaussian)

                dpg.add_input_float(label="Amplitude", width=UI_CONSTS.W_NUM_INP_SING_COL, tag="gauss_A")
                dpg.add_input_float(label="Mean", width=UI_CONSTS.W_NUM_INP_SING_COL, tag="gauss_mu")
                dpg.add_input_float(label="Standard deviation", width=UI_CONSTS.W_NUM_INP_SING_COL, tag="gauss_std")
                with dpg.group(horizontal=True):
                    dpg.add_button(label = "Add", callback=self.addGaussian)
                    dpg.bind_item_theme(dpg.last_item(), "button_theme")
                    dpg.add_button(label = "Delete", callback=self.removeGaussian)
                    dpg.bind_item_theme(dpg.last_item(), "button_theme")

                dpg.add_text("Attempt to fit model")
                dpg.add_button(label = "Fit") # TODO fit callback
                dpg.bind_item_theme(dpg.last_item(), "button_theme")

                # SAVING
                dpg.add_spacer(height=UI_CONSTS.H_COLL_HEAD_SPACER)
                dpg.add_text("Save model fit")
                dpg.add_input_text(hint="Model name", width=UI_CONSTS.W_TXT_INP, tag="model_fit_name")
                dpg.add_button(label = "Save") # TODO export callback
                dpg.bind_item_theme(dpg.last_item(), "button_theme")
            
            
            # DATA EDITING
            dpg.add_spacer(height=UI_CONSTS.H_COLL_HEAD_SPACER)
            with dpg.collapsing_header(label="Edit", default_open=True):
                dpg.add_text("Edit current observation")
                dpg.add_input_int(label="Smoothing", min_clamped=True, min_value=1, default_value=1, step=2, tag="editing_smoothing", width=UI_CONSTS.W_NUM_INP_SING_COL, callback=self.updateObservation)
            
                dpg.add_checkbox(label="Toggle linear/log scale", callback=self.updateObservation, tag="toggle_lin_log")


                # SAVING
                dpg.add_spacer(height=UI_CONSTS.H_COLL_HEAD_SPACER)
                with dpg.group(horizontal=True):
                    dpg.add_text("Save to new directory")
                    dpg.add_spacer(width=5)
                    dpg.add_button(label = "Browse", width=UI_CONSTS.W_TXT_INP, callback=lambda: dpg.show_item("export_dialog"))
                    dpg.bind_item_theme(dpg.last_item(), "button_theme")
                
                # File dialog
                with dpg.file_dialog(label = "Browse", directory_selector=True, show = False, 
                                    tag = "export_dialog", width=600, 
                                    height=400, default_path=os.getcwd(), 
                                    callback=lambda s, a, u: dpg.set_value("export_directory", UI_CONSTS.fileBrowserCallback(s, a, u)),
                                    cancel_callback=UI_CONSTS.fileBrowserCancelled):
                    pass
                dpg.add_input_text(hint="Directory", width=UI_CONSTS.W_TXT_INP, tag="export_directory")
                dpg.add_button(label="Save", callback=self.saveToFile)
                dpg.bind_item_theme(dpg.last_item(), "button_theme")
                
                dpg.add_text("Or override existing observation data")
                dpg.add_button(label="Override")
                dpg.bind_item_theme(dpg.last_item(), "button_theme")
    
    def addGaussian(self) -> None:
        '''
        Add Gaussian profile to model fit from parameters
        '''
        A = float(dpg.get_value("gauss_A"))
        mu = float(dpg.get_value("gauss_mu"))
        std = float(dpg.get_value("gauss_std"))

        self.gauss_A.append(A)
        self.gauss_mu.append(mu)
        self.gauss_std.append(std)

        # Update drowdown
        self.updateGaussianDropdown()
    
    def removeGaussian(self) -> None:
        '''
        Remove Gaussian profile from model fit from selected in dropdown
        '''
        selected = dpg.get_value("gaussian_dropdown")
        gauss_idx = int(selected[-1])-1

        del self.gauss_A[gauss_idx]
        del self.gauss_mu[gauss_idx]
        del self.gauss_std[gauss_idx]

        self.updateGaussianDropdown()
    
    def updateGaussianDropdown(self) -> None:
        '''
        Update Gaussians displayed in drowdown
        '''
        gaussians = [f"Gaussian {i+1}" for i in range(len(self.gauss_A))]
        dpg.configure_item("gaussian_dropdown", items=gaussians)
    
    def updateSelectedGaussian(self) -> None:
        '''
        Upon selection of a Gaussian profile in the dropdown, show parameters
        '''
        selected = dpg.get_value("gaussian_dropdown")
        gauss_idx = int(selected[-1])-1

        dpg.set_value("gauss_A", self.gauss_A[gauss_idx])
        dpg.set_value("gauss_mu", self.gauss_mu[gauss_idx])
        dpg.set_value("gauss_std", self.gauss_std[gauss_idx])

    def updateObservation(self) -> None:
        '''
        Update observation info fields and spectrum plot
        '''

        obs_path = dpg.get_value("observation_directory")

        # Some initial checking of the validation of the file
        if not os.path.isdir(obs_path):
            print("Not a valid file path!!")
            return
        
        self.observation = Observation(dir=obs_path)
        freqs, radial_vel, data = self.observation.readData()
        info = self.observation.readInfo()

        # Update table with observation information
        for i, k in enumerate(obs_kw_names):
            if info[k].size > 1:
                dat = f"{np.round(info[k][0], 4)}, {np.round(info[k][1], 4)}"
            else:
                dat = str(info[k])
            dpg.set_value(row_names[i]+"_value", dat)
        

        # Finally, update line series
        conv = int(dpg.get_value("editing_smoothing"))
        if conv > 1:
            data = DSP.applySmoothing(data, conv)
        
        if dpg.get_value("toggle_lin_log"):
            data = 10**(data/10) if np.mean(data) < 0 else 10*np.log10(data)
        
        updateLineSeries(xdata=freqs/10**6, ydata=data, vel=radial_vel)


    def saveToFile(self) -> None:
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
        file_name = dpg.get_value("observation_directory")[:-4]+"_EDITED.txt"
        new_obs = Observation(path=file_name, obs_time=obs_time, local_coord=obs_coord_azel,
                            eq_coord=obs_coord_eq, gal_coord=obs_coord_gal, lsr_corr=lsr_cor,
                            freqs=xdata, radial_vel=vel, data=ydata)

        new_obs.writeObservationFile()
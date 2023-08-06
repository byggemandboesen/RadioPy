import dearpygui.dearpygui as dpg
import numpy as np


def dataViewerWindow():
    '''
    Window of data viewer
    '''
    with dpg.child_window(width=-1):
        dpg.add_text("Data viewer")

        with dpg.plot(width=-1,height=-1, tag = "spectrum_plot", anti_aliased=True):
            dpg.add_plot_axis(dpg.mvXAxis, label = "Frequency", tag="x_axis")
            dpg.add_plot_axis(dpg.mvYAxis, label = "Flux", tag="y_axis")
            dpg.add_plot_legend()
            
            # And then add data to plot
            dpg.add_line_series(np.linspace(0, 1, 100), np.zeros(100), label="Data", parent="y_axis", tag="spectrum_line_series")

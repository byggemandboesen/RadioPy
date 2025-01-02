import dearpygui.dearpygui as dpg
import numpy as np

# TODO - Maybe remake into class

def dataViewerWindow():
    '''
    Window of data viewer
    '''
    with dpg.child_window(width=-1):
        dpg.add_text("Data viewer")

        with dpg.plot(width=-1,height=-1, tag = "spectrum_plot", anti_aliased=True):
            dpg.add_plot_axis(dpg.mvXAxis, label = "Frequency (MHz)", tag="x_axis")
            dpg.add_plot_axis(dpg.mvYAxis, label = "Intensity", tag="y_axis")
            dpg.add_plot_legend()
            
            # And then add data to plot
            dpg.add_line_series(np.linspace(0, 1, 100), np.zeros(100), label="Data", parent="y_axis", tag="spectrum_line_series")


def updateLineSeries(xdata: np.ndarray, ydata: np.ndarray, vel: np.ndarray) -> None:
    '''
    Update currently displayed line series
    '''
    dpg.set_value("spectrum_line_series", [xdata, ydata, vel])
    dpg.fit_axis_data('x_axis')
    dpg.fit_axis_data('y_axis')

import dearpygui.dearpygui as dpg

SPECTRAL_LINES = ["H1", "OH_1612", "OH_1665", "OH_1667", "OH_1720"]


def spectralLineWindow(pos: list = [420,20], w: int = 400, h: int = 500):
    with dpg.window(label= "Spectral line", width=w, height=h, no_close=True, pos=pos):
        
        with dpg.collapsing_header(label = "Data collection"):
            dpg.add_input_int(label = "Bins", default_value=4096, tag = "bins", width = -150, callback = updateTimeEstimate)
            dpg.add_input_int(label = "FFT average", default_value=1000, tag = "fft_num", width = -150, callback = updateTimeEstimate)
            dpg.add_input_int(label = "Median", default_value=0, tag = "median", width = -150, callback = updateTimeEstimate)
            
            # TODO Add tooltip to this one
            dpg.add_checkbox(label = "DC offset", default_value=False, tag = "dc_offset")

        with dpg.collapsing_header(label = "Object"):
            dpg.add_text("Select spectral line")
            # TODO - Think if there are more relevant info to store here
        
        dpg.add_spacer(height=5)
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
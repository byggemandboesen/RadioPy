import dearpygui.dearpygui as dpg

# Available spectral lines
SPECTRAL_LINES = {
    "H1, 1420MHz": "H1",
    "OH, 1612MHz": "OH_1612",
    "OH, 1665MHz": "OH_1665",
    "OH, 1667MHz": "OH_1667",
    "OH, 1720MHz": "OH_1720"
}

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
            dpg.add_combo(list(SPECTRAL_LINES.keys()), default_value=list(SPECTRAL_LINES.keys())[0], tag = "spectral_line")
            
            with dpg.group(horizontal=True):
                dpg.add_checkbox(label = "Correct for LSR", tag="lsr_correct", default_value=True)
                dpg.add_text("(?)", color=(0,0,255,255), tag = "lsr_tooltip")

            with dpg.tooltip("lsr_tooltip"):
                dpg.add_text("Correct radial velocity to the local standard of rest")
        

        # Run observation section
        dpg.add_spacer(height=5)
        dpg.add_button(label = "Run observation", callback=runObservation)
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


def runObservation():
    line = SPECTRAL_LINES[dpg.get_value("spectral_line")]
    print("Running observation...")

import sys
import dearpygui.dearpygui as dpg

import src.soapy as soapy

# TODO Probably make a separate UI for pulsar stuff I don't know yet
# TODO Get screen resolution to scale UI properly

# Run user interface
def runUI(sdr):
    dpg.create_context()
    dpg.create_viewport(title='RadioPy - By Victor Boesen', width=650, height=500)
    
    # Show window for each parameter category

    # Get sample rates and etc. from "sdr"

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    runUI()
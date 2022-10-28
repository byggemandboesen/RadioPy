import sys
import dearpygui.dearpygui as dpg

# TODO Probably make a separate UI for pulsar stuff I don't know yet
# TODO Get screen resolution to scale UI properly

import ui.modules.parameters.parameters as parameters
import ui.modules.editor.editor as editor


# Run user interface
def runUI():
    dpg.create_context()
    dpg.create_viewport(title='RadioPy - By Victor Boesen', width=1280, height=720)
    
    # Show module for each parameter category
    with dpg.window(label = "Modules", width=400, height=500, no_close=True, pos= [10,10]):
        parameters.parametersModule()
        editor.editorModule()

    # Get sample rates and etc. from "sdr"

    # Create editing module and live plot window

    # Maybe create window for pulsar stuff?


    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    runUI()
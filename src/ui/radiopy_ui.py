import sys
import dearpygui.dearpygui as dpg

# TODO Probably make a separate UI for pulsar stuff I don't know yet
# TODO Get screen resolution to scale UI properly

import ui.spectral_line.spectral_line_ui as lineUI
import ui.parameters.parameters as paramUI


# Run user interface
def runUI():
    dpg.create_context()
    dpg.create_viewport(title='RadioPy - By Victor Boesen', width=1280, height=720)
    
    # General parameters/options
    paramUI.parametersWindow()
    # with dpg.window(label = "Parameters", width=500, height=500, no_close=True, pos= [10,10]):
    #     parameters.parametersModule()
    #     editor.editorModule()
    
    # Spectral line window
    lineUI.spectralLineWindow()
    

    # Maybe create window for pulsar stuff?


    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    runUI()
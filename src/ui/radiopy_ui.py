import sys
import dearpygui.dearpygui as dpg

# Import UI components
import ui.spectral_line.spectral_line_ui as lineUI
import ui.parameters as paramUI


# Run user interface
def runUI():
    dpg.create_context()
    dpg.create_viewport(title='RadioPy - By Victor Boesen', width=830, height=520)
    
    # General parameters/options
    paramUI.parametersWindow()
    
    # Spectral line window
    lineUI.spectralLineWindow()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    runUI()
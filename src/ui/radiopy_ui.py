import sys
import dearpygui.dearpygui as dpg

# Import UI components
import ui.tabs.spectral_line_ui as LINE_UI
import ui.tabs.parameters as PARAM_UI
import ui.ui_constants as UI_CONSTS

# Run user interface
def runUI():
    dpg.create_context()
    dpg.create_viewport(title='RadioPy - By Victor Boesen', width=1225, height=625)
    
    with dpg.window(label="Main window", pos=[10,10], width=1200, height=600, no_title_bar=True):

        with dpg.group(horizontal=True):
            with dpg.child_window(width=400):
                with dpg.tab_bar(reorderable=True):
                    # General parameters/options
                    PARAM_UI.parametersTab()
                    
                    # Spectral line window
                    LINE_UI.spectralLineTab()

                    # Editor


            with dpg.child_window(width=-1):
                dpg.add_text("Data viewer")

    
    # Apply theme
    theme = UI_CONSTS.defaultTheme()
    dpg.bind_theme(theme)

    
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    runUI()
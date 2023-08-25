import sys
import dearpygui.dearpygui as dpg

# Import UI components
import ui.tabs.spectral_line_ui as LINE_UI
import ui.tabs.parameters as PARAM_UI
import ui.tabs.editor as EDITOR_UI
import ui.tabs.analysis as ANALYSIS_UI

import ui.tabs.info as INFO
import ui.dataviewer as DATAVIEWER

import ui.ui_constants as UI_CONSTS

# Run user interface
def runUI():
    dpg.create_context()
    dpg.create_viewport(title='RadioPy - By Victor Boesen', width=1400, height=800)
    
    with dpg.window(label="Main window", no_title_bar=True) as main_window:

        with dpg.group(horizontal=True):
            with dpg.child_window(width=400):
                with dpg.tab_bar(reorderable=True):
                    # General parameters/options
                    PARAM_UI.parametersTab()
                    
                    # Spectral line
                    LINE_UI.spectralLineTab()

                    # Editor (Consider merging editor with spectral line tab)
                    # EDITOR_UI.editorTab()

                    # Analysis
                    ANALYSIS_UI.analysisTab()

                    # Info
                    INFO.infoTab()


            DATAVIEWER.dataViewerWindow()

    
    # Apply theme
    theme = UI_CONSTS.defaultTheme()
    dpg.bind_theme(theme)

    dpg.set_primary_window(main_window, True)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    runUI()
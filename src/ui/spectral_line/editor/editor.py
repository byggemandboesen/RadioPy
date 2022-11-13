import dearpygui.dearpygui as dpg
import pandas as pd
import json


def editorModule():
    '''
    Module for observation data viewing and editing
    '''
    with dpg.collapsing_header(label = "Editor"):
        dpg.add_text("Load and edit observation data")

        dpg.add_text("Load main file")
        with dpg.group(horizontal=True):
            dpg.add_input_text(hint = "Main file path", width = -200, tag = "main_path", callback = pathChanged)
            dpg.add_button(label = "Browse", callback=lambda: dpg.show_item("main_dialog"))
            
            # File dialog
            with dpg.file_dialog(label = "Browse", directory_selector= False, show = False, tag = "main_dialog", callback=fileDialogCallback):
                dpg.add_file_extension(".csv")
            
        dpg.add_text("Load secondary file")
        with dpg.group(horizontal=True):
            dpg.add_input_text(hint = "Secondary file path", width = -200, tag = "secondary_path", callback = pathChanged)
            dpg.add_button(label = "Browse", callback=lambda: dpg.show_item("secondary_dialog"))
            
            # File dialog
            with dpg.file_dialog(label = "Browse", directory_selector= False, show = False, tag = "secondary_dialog", callback=fileDialogCallback):
                dpg.add_file_extension(".csv")
        

        dpg.add_spacer(height=5)

        # Show observaiton info in table
        with dpg.tree_node(label = "File info"):
            dpg.add_text("Info about observation")
            
            dpg.add_spacer(height=5)
            with dpg.table(tag = "info_table", header_row=True, borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True, resizable=True):
                dpg.add_table_column(label = "RA/Dec")
                dpg.add_table_column(label = "Lon/Lat")
                dpg.add_table_column(label = "Spectral line")
                dpg.add_table_column(label = "Time")
                dpg.add_table_column(label = "LSR correction")
                with dpg.table_row(tag = "info_row"):
                    dpg.add_text("", tag = "Eq_coords")
                    dpg.add_text("", tag = "Gal_coords")
                    dpg.add_text("", tag = "Spectral_line")
                    dpg.add_text("", tag = "Observation_time")
                    dpg.add_text("", tag = "LSR_correction")

        # Show editing features
        with dpg.tree_node(label = "Edit"):
            dpg.add_text("Edit loaded data")



def updateObservationInfo():
    '''
    Update table with info from loaded observation
    '''
    path = dpg.get_value("main_path")
    data = pd.read_csv(path)

    Eq_coords = [data["Eq_coords"][0], data["Eq_coords"][1]]
    Gal_coords = [data["Gal_coords"][0], data["Gal_coords"][1]]
    Spectral_line = data["Spectral_line"][0]
    Observation_time = data["Observation_time"][0]
    LSR_correction = data["LSR_correction"][0]

    # Finally, update values in table
    dpg.set_value("Eq_coords", Eq_coords)
    dpg.set_value("Gal_coords", Gal_coords)
    dpg.set_value("Spectral_line", Spectral_line)
    dpg.set_value("Observation_time", Observation_time)
    dpg.set_value("LSR_correction", LSR_correction)


def pathChanged():
    '''
    Handle path typed in text field
    '''
    print("Path changed")


def fileDialogCallback(sender, app_data):
    '''
    Parse file path from file dialog
    '''
    
    # print(f"Sender: {sender}, data: {app_data}")
    if sender == "main_dialog":
        dpg.set_value("main_path", app_data["file_path_name"])
        updateObservationInfo()
    elif sender == "secondary_dialog":
        dpg.set_value("secondary_path", app_data["file_path_name"])
    else:
        print("Unexpected error occured...")
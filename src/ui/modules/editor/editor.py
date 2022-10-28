import dearpygui.dearpygui as dpg
import pandas as pd
import json


def editorModule():
    '''
    Module for observation data viewing and editing
    '''
    with dpg.collapsing_header(label = "Editor"):
        dpg.add_text("Load and edit observation data")

        dpg.file_dialog(label = "Browse")
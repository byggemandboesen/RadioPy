import dearpygui.dearpygui as dpg
import pandas as pd
import os

def analysisTab():
    '''
    Module for analysing data files - Gaussian fitting etc.
    '''
    with dpg.tab(label="Analysis"):
        dpg.add_text("Load data for analysis")

        # Collapsing header for spectral line and pulsar
        
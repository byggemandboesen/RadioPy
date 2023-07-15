import dearpygui.dearpygui as dpg
import textwrap

def infoTab():
    '''
    Tab with information about RadioPy
    '''

    with dpg.tab(label="?"):
        dpg.add_text("About RadioPy")

        info_text = textwrap.dedent('''
        RadioPy is developed by Victor Boesen - a student at the Technical University of Denmark.

        For any questions, reach out to me on GitHub or on twitter, @byggemandboesen and @victor_boesen respectively.
        ''')
        dpg.add_text(info_text, wrap=350)

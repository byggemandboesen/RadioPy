import dearpygui.dearpygui as dpg


def defaultTheme():
    '''
    The theme of the application
    '''
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
        
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (15, 86, 136, 175))
        
    return global_theme


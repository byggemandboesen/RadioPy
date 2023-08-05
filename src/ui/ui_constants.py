import dearpygui.dearpygui as dpg

W_NUM_INP_SING_COL = -150
W_NUM_INP_DOUB_COL = 150

W_TXT_INP = -150

H_COLL_HEAD_SPACER = 5


def defaultTheme():
    '''
    The theme of the application
    '''
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 5)

            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 5, 5)
        
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (15, 86, 136, 175))
        
        with dpg.theme_component(dpg.mvCollapsingHeader):
            dpg.add_theme_color(dpg.mvThemeCol_Header, (*(70,)*3, 255))
        
    return global_theme


def fileBrowserCallback():
    '''
    Callback for file browser
    '''
    return

def fileBrowserCancelled():
    '''
    Callback for cancelled file browsing
    '''
    return

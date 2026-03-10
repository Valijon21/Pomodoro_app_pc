import uiautomation as auto
import time

def get_browser_urls():
    urls = []
    # Search for Chrome windows
    # Desktop is the root
    windows = auto.GetRootControl().GetChildren()
    for win in windows:
        if win.ControlType == auto.ControlType.WindowControl:
            name = win.Name
            className = win.ClassName
            if "Chrome_WidgetWin_1" in className or "MozillaWindowClass" in className:
                # Find edit control
                try:
                    edit = win.EditControl()
                    if edit.Exists(0, 0):
                        urls.append((name, edit.GetValuePattern().Value))
                except Exception as e:
                    urls.append((name, str(e)))
    return urls

print(get_browser_urls())

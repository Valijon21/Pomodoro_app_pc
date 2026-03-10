import uiautomation as auto
import time
import pygetwindow as gw

start = time.time()
for window in gw.getAllWindows():
    if not window.title: continue
    title_lower = window.title.lower()
    if any(b in title_lower for b in ['chrome', 'edge', 'firefox', 'brave', 'yandex']):
        win = auto.WindowControl(Name=window.title)
        if win.Exists(0, 0):
            edit = win.EditControl()
            if edit.Exists(0, 0):
                url = edit.GetValuePattern().Value
                print(f"[{time.time()-start:.2f}s] Found URL for {window.title}: {url}")
print(f"Total time: {time.time()-start:.2f}s")

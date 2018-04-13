# import win32api  
# import win32con
import win32gui
# import datetime

# messageHandle = win32gui.FindWindow('#32770', None)
# print(datetime.datetime.now(),'--',messageHandle)
def gethWnd(size=[]):
    hWndList = []
    win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), hWndList)
    # print(hWndList)
    for i in hWndList:
        if len(size) > 1:
            l, t, r, b = win32gui.GetWindowRect(i)
            if r-l == size[0] and b-t == size[1]:
                return i

if __name__ == '__main__':

    a = gethWnd([297,229])
    print(a)
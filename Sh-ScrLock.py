''' -----------------------
program: Sh-ScrLock
version: 2.2.20210505

This Python program switches On/Off Screen Saver and Screen Locker in Windows 10 via system register.
May be convenient when you use your PC in different environments (like office and home).

command line: python.exe Sh-ScrLock.py [-on | -off | -ask [-silent | -autoclose [seconds]]]
------------------------'''

from winreg import *
from tkinter import *  
import sys
import winsound
import os.path

reg_vals = [
    [HKEY_CURRENT_USER, r"Control Panel\Desktop", "ScreenSaveActive", "0", "1", REG_SZ],
    [HKEY_CURRENT_USER, r"Control Panel\Desktop", "ScreenSaverIsSecure", "0", "1", REG_SZ],
    [HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "InactivityTimeOutSecs", 0, 900, REG_DWORD]
]

class ShWinReg:
    def __init__(self):
        pass

    def readValue(self, key, sub_key, value_name):
        keyHandle = OpenKey(key, sub_key, 0, KEY_READ)
        regValue_val = QueryValueEx(keyHandle, value_name)
        CloseKey(keyHandle) 
        return regValue_val

    def writeValue(self, key, sub_key, value_name, value_val, value_type):
        exitCode = 1
        try:
            keyHandle = OpenKey(key, sub_key, 0, KEY_SET_VALUE)
            SetValueEx(keyHandle, value_name, 0, value_type, value_val )
            CloseKey(keyHandle)
        except:
            exitCode = 0
        return exitCode


class ScrLockGUI:
    def __init__(self, arrayRegVals, objWinReg):
        self.objWinReg = objWinReg
        self.arrayRegVals = arrayRegVals
        self.window = Tk()  
        self.window.title("Sh ScrLock")
        self.window.minsize(width=400, height=50)
        self.window.iconbitmap(os.path.dirname(__file__)+ "\\Sh-ScrLock.ico")
        self.panel_buttons()
        self.panel_info("Check Registry")
        #- put window into screen center
        self.x = (self.window.winfo_screenwidth() - self.window.winfo_reqwidth()) / 2
        self.y = (self.window.winfo_screenheight() - self.window.winfo_reqheight()) / 2
        self.window.wm_geometry("+%d+%d" % (self.x, self.y))
        self.window.protocol('WM_DELETE_WINDOW', self.cmd_close)
        self.silentRun = 0
        self.autoclose = 0
        self.autoclose_sec = 0
        self.window.withdraw()
    
    def _write_reg_values(self, flagOn):
        exitCode = 1
        for rec in self.arrayRegVals:
            if not self.objWinReg.writeValue (rec[0], rec[1], rec[2], rec[4] if flagOn else rec[3], rec[5]):
                exitCode = 0
        return exitCode
    
    def cmd_close(self):
        self.window.destroy()

    def cmd_on(self):
        self._update_panel_info([1,self._write_reg_values(1)])
    
    def cmd_off(self):
        self._update_panel_info([0,self._write_reg_values(0)])

    def panel_buttons(self):
        self.frameButtons = Frame(self.window)
        self.frameButtons.pack(side=BOTTOM, expand=YES, fill=BOTH)
        self.lblFake = Label(self.frameButtons, width=4)
        self.lblFake.pack(side=RIGHT)
        self.buttonClose = Button(self.frameButtons, text="Close", width=10, command=self.cmd_close)
        self.buttonClose.pack(side=RIGHT, padx=5, pady=5)
        self.buttonOff = Button(self.frameButtons, text="Switch OFF", width=10, command=self.cmd_off)
        self.buttonOff.pack(side=RIGHT, padx=5, pady=5)
        self.buttonOn = Button(self.frameButtons, text="Switch ON", width=10, command=self.cmd_on)
        self.buttonOn.pack(side=RIGHT, padx=5, pady=5)

    def _update_panel_info(self, opStatus):
        txtAction = ["Switch OFF", "Switch ON"]
        txtError = [". ERROR writing Registry!", ""]
        txtCloseSeconds = ("\n(Auto-Close in " + str(self.autoclose_sec) + 
            " seconds)") if self.autoclose else ""
        winsound.MessageBeep(winsound.MB_OK)
        self.frameInfo.destroy()
        self.panel_info(txtAction[opStatus[0]] + txtError[opStatus[1]] + txtCloseSeconds)
    
    def panel_info(self, strTxt):
        self.frameInfo = LabelFrame(self.window, bd=4, relief=RIDGE, text="System Current State:")
        self.frameInfo.pack(side=TOP, expand=YES, fill=BOTH) 
        lbl = Label(self.frameInfo, text = "Performed operation: " + strTxt)
        lbl.pack(side=TOP, anchor="c", padx=25)  
        for rec in self.arrayRegVals:
            registryInfoText = rec[2] + ": \t" + str(self.objWinReg.readValue(rec[0], rec[1], rec[2])[0])
            lbl = Label(self.frameInfo, text = registryInfoText)
            lbl.pack(side=TOP, anchor="w", padx=25)
        lbl = Label(self.frameInfo, text = "")
        lbl.pack(side=TOP, anchor="w", padx=25)

    def main_cycle(self):
        if self.silentRun: sys.exit()
        if self.autoclose:
            self.window.after((self.autoclose_sec * 1000), self.cmd_close)
        self.window.deiconify()
        self.window.mainloop()


def check_mode():
    try:
        opMode = sys.argv[1]
        if (opMode != "-on") and (opMode != "-off"): opMode = "-ask"
    except:
        opMode = "-ask"
    silentMode = 0
    autoCloseMode = 0
    autoClose_sec = 5
    try:
        if (sys.argv[2] == "-silent") and (opMode != "-ask"): 
            silentMode = 1
        elif (sys.argv[2] == "-autoclose"):
            autoCloseMode = 1
            try:
                autoClose_sec = int(sys.argv[3])
            except:
                pass
    except:
        pass

    return opMode, silentMode, autoCloseMode, autoClose_sec


def main():

    runMode = check_mode()
    winRegistry = ShWinReg()
    objGUI = ScrLockGUI(reg_vals, winRegistry)

    if runMode[1]: objGUI.silentRun = 1
    if runMode[2]: objGUI.autoclose = 1
    if runMode[3]: objGUI.autoclose_sec = runMode[3]

    if runMode[0] == "-on":
         objGUI.cmd_on()
    elif runMode[0] == "-off":
        objGUI.cmd_off()
    else:
        pass #command "ask"

    objGUI.main_cycle()


if __name__ == "__main__":
    main()



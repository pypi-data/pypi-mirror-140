import win32com.client

import subprocess
import time

SAP_GUI_PATH = r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"


class SapGui:

    def __init__(self, nombre_conexion="SAP PRO"):

        self.process = subprocess.Popen(SAP_GUI_PATH)
        time.sleep(10)

        self.SapGuiAuto = win32com.client.GetObject("SAPGUI")
        if not type(self.SapGuiAuto) == win32com.client.CDispatch:
            return

        self.application = self.SapGuiAuto.GetScriptingEngine
        if not type(self.application) == win32com.client.CDispatch:
            self.SapGuiAuto = None
            return

        # connection = application.Children(0)
        self.connection = self.application.OpenConnection(nombre_conexion, True)
        if not type(self.connection) == win32com.client.CDispatch:
            self.application = None
            self.SapGuiAuto = None
            return

        self.session = self.connection.Children(0)
        if not type(self.session) == win32com.client.CDispatch:
            self.connection = None
            self.application = None
            self.SapGuiAuto = None
            return

    def login(self, user, password):
        self.session.findById("wnd[0]/usr/txtRSYST-BNAME").text = user
        self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = password
        self.session.findById("wnd[0]").sendVKey(0)
        self.session.findById("wnd[0]").maximize()

    def logout(self):
        self.session.findById("wnd[0]").close()
        self.session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()

    def close(self):
        self.connection = None
        self.application = None
        self.SapGuiAuto = None
        self.session = None
        self.process.kill()


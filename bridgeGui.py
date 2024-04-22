#!/usr/bin/python
# -*- coding: <<encoding>> -*-
#-------------------------------------------------------------------------------
#   BridgeGui
# 
#-------------------------------------------------------------------------------

#import wxversion
# wxversion.select("2.8")
from typing import Type
import wx, wx.html
import sys
import subprocess
import re

aboutText = """<p>This is a small programm to easily create bridge interfaces for VM's
    Use with caution. This program needs administrator access. <a href="https://github.com/Spuk1/bridgeGui">Source</a>
</p>""" 

class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600,400)):
        wx.html.HtmlWindow.__init__(self,parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())
        
class AboutBox(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "About <<BridgeGui>>",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER|
                wx.TAB_TRAVERSAL)
        hwin = HtmlWindow(self, -1, size=(400,200))
        vers = {}
        vers["python"] = sys.version.split()[0]
        vers["wxpy"] = wx.VERSION_STRING
        hwin.SetPage(aboutText % vers)
        btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth()+25, irep.GetHeight()+10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()

class Frame(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(800,400))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.splitter = wx.SplitterWindow(self)
        self.splitter.SetSize(self.GetSize())
        self.splitter.SetSashGravity(0.5)
        self.splitter.SetMinimumPaneSize(100)
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menuBar.Append(menu, "&File")
        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        menuBar.Append(menu, "&Help")
        self.SetMenuBar(menuBar)
        
        self.statusbar = self.CreateStatusBar()

        self.panel = wx.Panel(self.splitter)
        
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.logger = wx.LogGui()
        box = wx.BoxSizer(wx.VERTICAL)
        self.hbox.Add(box,1, wx.Left|wx.EXPAND, 10)
        box2 = wx.BoxSizer(wx.VERTICAL)
        self.hbox.Add(box2,1, wx.Right|wx.EXPAND, 10)
        self.scrollbox = wx.ScrolledWindow(self.splitter)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.scrollbox.SetSizer(self.sizer)

        # box2.Add(self.scrollbox)
        m_text = wx.StaticText(self.scrollbox, -1, "Log:")
        # m_text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        # m_text.SetSize(m_text.GetBestSize())
        self.sizer.Add(m_text, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
        self.panel.SetSizer(self.hbox)
        # self.panel.SetSizer(box)
        self.panel.Layout()
        self.loadInterfaces()
        self.selected = self.intList[0]
        choices = [x[0] for x in self.intList if len(x) > 1]
        self.comboBox = wx.Choice(self.panel,-1, (85,15), choices=choices)
        self.comboBox.Bind(wx.EVT_CHOICE, self.onChoice)
        self.comboBox.SetSelection(0)
        box.Add(self.comboBox, 0, wx.ALL, 10)
        self.bridge  = wx.TextCtrl(self.panel, -1)
        box.Add(self.bridge, 0 , wx.ALL, 10)
        self.create = wx.Button(self.panel, wx.ID_CLOSE, "Create Bridge")
        self.create.Bind(wx.EVT_BUTTON, self.OnCreate)
        box.Add(self.create, 0, wx.ALL, 10)
        self.delete = wx.Button(self.panel, wx.ID_CLOSE, "Delete Bridges")
        self.delete.Bind(wx.EVT_BUTTON, self.OnDeleteSelectedBridge)
        box2.Add(self.delete, 0, wx.ALL, 10)
        self.splitter.SplitVertically(self.panel, self.scrollbox)
        self.splitter.UpdateSize()

       

    def loadInterfaces(self):
        output = subprocess.getstatusoutput(f'ip addr')[1]
        self.intList = []
        i = 0
        count = 1
        while i != -1:
            new_i = output.find(f'{count}: ')
            interface = []
            string = output[i:new_i]
            if len(string):
                interface.append(string.split(":")[1].strip())
                interface += re.findall(r'\b(?:[1-2]?[0-9]{1,2}\.){3}[1-2]?[0-9]{1,2}\b', string)
                if len(interface) > 0:
                    self.intList.append(interface)
            i=new_i
            count+=1

    def onChoice(self, event):
        list = [x for x in self.intList if len(x) > 1]
        self.selected = list[self.comboBox.GetSelection()][:2]

    def OnDeleteSelectedBridge(self, event):
        success = subprocess.getstatusoutput(f"sudo ip link delete {self.selected[0]}")
        if success[0] == 0:
            dlg = wx.MessageBox("All Bridges deleted")

    def OnClose(self, event):
        dlg = wx.MessageDialog(self, 
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()

    def log(self, text):
        text = wx.StaticText(self.scrollbox, -1, "<<    " +  text)
        self.sizer.Add(text, 0, wx.ALL, 5)
        self.sizer.RepositionChildren(wx.Size(0,0))


    def OnCreate(self, event):
        self.log(f"interface '{self.selected[0]}' with ip '{self.selected[1]}' to '{self.bridge.GetValue()}'")
        output = subprocess.getstatusoutput(f'ip route')[1].splitlines()[0]
        interface = re.findall(r'\b(?:[1-2]?[0-9]{1,2}\.){3}[1-2]?[0-9]{1,2}\b', output)[0]
        exists = [x[0] for x in self.intList]
        proc = subprocess.getstatusoutput(f"sudo ip link add {self.bridge.GetLineText(0)} type bridge")
        if self.bridge.GetLineText(0) in exists:
            self.log("Bridge allready exists. Relinking...")
        elif proc[0] == 0:
            self.log("Creating Bridge successfull. Continue")
        else:
            self.log("Bridge could not be created. Abort!")
            return
        proc = subprocess.getstatusoutput(f"sudo ip link set {self.selected[0]} master {self.bridge.GetLineText(0)}")
        if proc[0] == 0:
            self.log("Bridge set to master")
        else:
            self.log(proc[1])
            return
        proc = subprocess.getstatusoutput(f"sudo ip addr flush {self.selected[0]}")
        if proc[0] == 0:
            self.log("Selected Interface flushed. Continue")
        else:
            self.log("Could not flush interface. Abort!")
            return
        proc = subprocess.getstatusoutput(f"sudo ip addr add {self.selected[1]}/24 dev {self.bridge.GetLineText(0)}")
        if proc[0] == 0:
            self.log("Set bridge ip address. Continue")
        else:
            self.log("Bridge ip address could not be set. Abort!")
            return
        proc = subprocess.getstatusoutput(f"sudo ip link set {self.bridge.GetLineText(0)} up")
        if proc[0] == 0:
            self.log("Turned on bridge interface. Continue")
        else:
            self.log("Bridge interface couldnt be started. Abort!")
            return
        proc = subprocess.getstatusoutput(f"sudo ip route add default via {interface}")
        if proc[0] == 0:
            self.log(f"Route ip address '{output}' set. Continue")
        else:
            self.log("Route ip address could not be set Abort!")
            return
        self.log(f"Bridge '{self.bridge.GetLineText(0)}' was created. Enjoy!")

    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()  

app = wx.App(redirect=True)   # Error messages go to popup window
top = Frame("BridgeGui")
top.Show()
app.MainLoop()
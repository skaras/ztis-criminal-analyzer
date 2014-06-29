# -*- coding: utf-8 -*- 

import wx
from ztis.gui.gui import *
from ztis.database.database import *


if __name__ == '__main__':
    
    if "unicode" in wx.PlatformInfo:
        print "has unicode"
    
    app = wx.App(redirect=True, filename="ztis_log.txt")
    frame = MainFrame(None)
    
    frame.Show()
    app.MainLoop()

# -*- coding: utf-8 -*- 


import wx
import wx.xrc

from ztis.database.database import *
from ztis.importer.import_all import *
from ztis.extractor.extract import *
from ztis.exporter.export import *



class MainFrame ( wx.Frame ):
    
    database = Database()
    extractor = Extractor()
    exporter = Exporter()
    
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"ZTIS Criminal Analyzer", pos = wx.DefaultPosition, size = wx.Size( 600,460 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
        
        bSizer2 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Spółki:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        bSizer2.Add( self.m_staticText4, 0, wx.ALL, 5 )
        
        m_companiesChoices = []
        self.m_companies = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_companiesChoices, 0 )
        bSizer2.Add( self.m_companies, 1, wx.ALL|wx.EXPAND, 5 )
        
        self.m_import = wx.Button( self, wx.ID_ANY, u"Importuj dane", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( self.m_import, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
        
        bSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )
        
        bSizer3 = wx.BoxSizer( wx.VERTICAL )
        
        m_criterionChoices = [ u"Największa wartość", u"Największy wzrost" ]
        self.m_criterion = wx.RadioBox( self, wx.ID_ANY, u"Kryterium", wx.DefaultPosition, wx.DefaultSize, m_criterionChoices, 1, wx.RA_SPECIFY_COLS )
        self.m_criterion.SetSelection( 0 )
        bSizer3.Add( self.m_criterion, 1, wx.ALL|wx.EXPAND, 5 )
        
        m_informationTypeChoices = [ u"Przychód netto", u"Zysk netto", u"Przepływ netto", u"Przepływ z dział. operacyjnej", u"Przepływ z dział. inwestycyjnej", u"Przepływ z dział. finansowej", u"Aktywa", u"Zobowiązania długoterminowe", u"Zobowiązania krótkoterminowe" ]
        self.m_informationType = wx.RadioBox( self, wx.ID_ANY, u"Typ informacji:", wx.DefaultPosition, wx.DefaultSize, m_informationTypeChoices, 1, wx.RA_SPECIFY_COLS )
        self.m_informationType.SetSelection( 0 )
        bSizer3.Add( self.m_informationType, 0, wx.ALL|wx.EXPAND, 5 )
        
        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"Analizowany rok:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        bSizer3.Add( self.m_staticText2, 0, wx.ALL, 5 )
        
        self.m_year = wx.TextCtrl( self, wx.ID_ANY, u"2005", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE )
        bSizer3.Add( self.m_year, 0, wx.ALL|wx.EXPAND, 5 )
        
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Maks. liczba wyników:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        bSizer3.Add( self.m_staticText3, 0, wx.ALL, 5 )
        
        self.m_maxResults = wx.TextCtrl( self, wx.ID_ANY, u"5", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE )
        bSizer3.Add( self.m_maxResults, 0, wx.ALL|wx.EXPAND, 5 )
        
        self.m_export = wx.Button( self, wx.ID_ANY, u"Eksportuj", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer3.Add( self.m_export, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
        
        bSizer1.Add( bSizer3, 1, wx.EXPAND, 5 )
        
        self.SetSizer( bSizer1 )
        self.Layout()
        
        self.Centre( wx.BOTH )
        
        
        # events
        
        self.m_import.Bind(wx.EVT_BUTTON, self.on_import)
        self.m_export.Bind(wx.EVT_BUTTON, self.on_export)
        
        
        # init
        self.refresh_companies()
    
    
    def refresh_companies(self):
        self.m_companies.Clear()
        
        companies = self.database.get_all(Company)
        
        for company in companies:
            self.m_companies.Append(company.name)
    
    
    def on_import(self, event):
        self.SetTitle(u"ZTIS Criminal Analyzer - importowanie spółek...")
        
        num = import_all(self.database)
        
        dlg = wx.MessageDialog(self, u"Zaimportowano " + str(num) + u" spółek", u"Import", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
        self.SetTitle(u"ZTIS Criminal Analyzer")
        
        self.refresh_companies()
    
    
    def on_export(self, event):
        
        year = max_results = 0
        
        try:
            year = int(self.m_year.GetValue())
        except:
            dlg = wx.MessageDialog(self, u"Nieprawidłowy format roku", u"Błąd", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        try:
            max_results = int(self.m_maxResults.GetValue())
        except:
            dlg = wx.MessageDialog(self, u"Nieprawidłowa maksymalna liczba wyników", u"Błąd", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        companies_ids = ()
        
        information_type = criterions[self.m_informationType.GetSelection()]
        
        if self.m_criterion.GetSelection() == 0:
            companies_ids = self.extractor.maxval(information_type, year, max_results)
        elif self.m_criterion.GetSelection() == 1:
            companies_ids = self.extractor.maxdiff(information_type, year, max_results)
        
        companies = self.extractor.ids_to_companies(companies_ids)
        
        if len(companies) == 0:
            dlg = wx.MessageDialog(self, u"Nie znaleziono spółek spełniających to kryterium", u"Błąd", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        self.exporter.export(companies, "alamakota.xml")
        
        dlg = wx.MessageDialog(self, u"Eksportowanie zakończone", u"Eksport", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        pass
    
    
    
    def __del__( self ):
        pass












if __name__ == '__main__':
    
    if "unicode" in wx.PlatformInfo:
        print "has unicode"
    
    app = wx.App(redirect=True, filename="ztis_log.txt")
    frame = MainFrame(None)
    
    frame.Show()
    app.MainLoop()

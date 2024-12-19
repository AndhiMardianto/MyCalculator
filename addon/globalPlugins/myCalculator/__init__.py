# NVDA Addon: My Calculator 
# Released under the GNU General Public License v2 
# Copyright (C) 2024 Andhi Mardianto

import globalPluginHandler
import ui
import re

import api
import tones
import addonHandler
addonHandler.initTranslation()

import wx
import gui
from keyboardHandler import KeyboardInputGesture
from scriptHandler import script

# Variabel global untuk menyimpan referensi dialog
showDialog = None

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self):
        super().__init__()

    @script(
        description=_("Open My Calculator dialog"),
        category=_("MyCalculator"),
        gesture="kb:nvda+shift+m"
    )
    def script_start(self, gesture):
        self.run(None)

    def run(self, event):
        global showDialog
        if not showDialog:
            showDialog = MainDialog(gui.mainFrame)
            showDialog.CenterOnScreen()
            showDialog.Raise()
        else:
            showDialog.Raise()

class MainDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="My Calculator", size=(600, 300))

        # Panel utama untuk elemen dialog
        panel = wx.Panel(self)

        # Layout komponen di dalam dialog
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Label dan input untuk operasi aritmatika
        sizer.Add(wx.StaticText(panel, label=_("Calculation Input")), 0, wx.ALL, 5)
        self.number1 = wx.TextCtrl(panel, size=(350, 25))
        self.number1.SetBackgroundColour("#f0f8ff")
        self.number1.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.number1.Bind(wx.EVT_TEXT, self.hitung)
        sizer.Add(self.number1, 0, wx.EXPAND | wx.ALL, 5)

        # Label dan input untuk menampilkan hasil
        sizer.Add(wx.StaticText(panel, label=_("Result")), 0, wx.ALL, 5)
        self.re = wx.TextCtrl(panel, size=(350, 100), style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_READONLY)
        self.re.SetBackgroundColour("#e6ffe6")
        self.re.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizer.Add(self.re, 1, wx.EXPAND | wx.ALL, 5)

        # Tombol Copy
        copy_button = wx.Button(panel, label=_("Copy"))
        copy_button.Bind(wx.EVT_BUTTON, self.periksa)
        copy_button.Bind(wx.EVT_CHAR_HOOK, self.onEnterForCopy)
        sizer.Add(copy_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        panel.SetSizer(sizer)

        # Bind event untuk Escape dan Enter
        self.Bind(wx.EVT_CHAR_HOOK, self.close)

        # Fokus ke input saat dialog muncul
        self.Bind(wx.EVT_SHOW, self.tampilkan)

        self.Show()

    def tampilkan(self, event):
        self.number1.SetFocus()

    def close(self, event):
        k = event.GetKeyCode()
        if k == wx.WXK_ESCAPE:
            self.Destroy()
        elif k in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.re.SetFocus()
        else:
            event.Skip()

    def onEnterForCopy(self, event):
        if event.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.periksa(event)
        event.Skip()

    def periksa(self, event):
        if not self.number1.Value:
            ui.message(_("Input is empty, cannot copy"))
            tones.beep(440, 100)
        else:
            if api.copyToClip(self.re.Value):
                ui.message(_("Copied"))

    def hitung(self, event):
        self.re.Value = ""
        expression = self.number1.Value

        # Mengganti 'x' dengan '*' dan ':' dengan '/' untuk operasi kali dan bagi
        expression = re.sub(r"[xX]", "*", expression).replace(":", "/")

        # Validasi input hanya angka dan simbol aritmatika
        if not all(char.isdigit() or char in "+-*/(). " for char in expression):
            ui.message(_("Invalid input, only numbers and arithmetic symbols allowed"))
            tones.beep(440, 100)
            expression = expression[:-1]
            self.number1.Value = expression
            self.number1.SetInsertionPoint(len(expression))
            return

        # Validasi aturan prioritas operasi matematika (BODMAS/PEMDAS)
        if re.search(r"\d+\s*[\+\-]\s*\d+\s*[\*/]", expression):
            ui.message(_("Invalid format. Please follow the standard arithmetic order."))
            self.re.Value = "Error! Invalid Format"
            tones.beep(440, 300)
            return

        try:
            # Evaluasi ekspresi yang valid
            num1 = eval(expression)
            self.re.Value = str(num1)
            tones.beep(750, 50)
        except:
            self.re.Value = _("Error! Check Input")
            tones.beep(440, 300)
            
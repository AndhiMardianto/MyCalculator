# NVDA Addon: My Calculator 
# Released under the GNU General Public License v2 
# Copyright (C) 2024 - 2025 Andhi Mardianto

import globalPluginHandler
import ui
import re
import math
import api
import tones
import addonHandler
import wx
import gui
from .help import show_calculator_help
from .scientific import DialogScientific
from .conversion import DialogConversion, tampilkan_tanggal_hijriah
from keyboardHandler import KeyboardInputGesture
from scriptHandler import script
addonHandler.initTranslation()

# Variabel global untuk menyimpan referensi dialog
showDialog = None

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self):
        super().__init__()

    @script(
        description=_("Say Hijriah date"),
        category=_("MyCalculator"),
        gesture="kb:nvda+shift+h"
    )
    def script_hijriah(self, gesture):
        conversion.tampilkan_tanggal_hijriah()

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
        super().__init__(parent, title="My Calculator", size=(800, 400))

        # Variabel untuk menyimpan riwayat
        self.history = []
        self.calculationMode = "standard"  # Default mode

        # Panel utama untuk elemen dialog
        panel = wx.Panel(self)

        # Layout komponen di dalam dialog
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Panel kiri untuk input dan hasil
        leftSizer = wx.BoxSizer(wx.VERTICAL)

        # Label dan input untuk operasi aritmatika
        leftSizer.Add(wx.StaticText(panel, label=_("Calculation Input")), 0, wx.ALL, 5)
        self.number1 = wx.TextCtrl(panel, size=(350, 25))
        self.number1.SetBackgroundColour("#f0f8ff")
        self.number1.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.number1.Bind(wx.EVT_CHAR_HOOK, self.onKeyPressed)
        self.number1.Bind(wx.EVT_TEXT, self.onTextChanged)
        leftSizer.Add(self.number1, 0, wx.EXPAND | wx.ALL, 5)

        # Label dan input untuk menampilkan hasil
        leftSizer.Add(wx.StaticText(panel, label=_("Result")), 0, wx.ALL, 5)
        self.re = wx.TextCtrl(panel, size=(350, 100), style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_READONLY)
        self.re.SetBackgroundColour("#e6ffe6")
        self.re.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        leftSizer.Add(self.re, 1, wx.EXPAND | wx.ALL, 5)

        # Tombol Copy
        copy_button = wx.Button(panel, label=_("Copy"))
        copy_button.Bind(wx.EVT_BUTTON, self.salin)
        leftSizer.Add(copy_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # Tombol Standar
        standard_button = wx.Button(panel, label=_("Standar"))
        standard_button.Bind(wx.EVT_BUTTON, self.set_standard_mode)
        leftSizer.Add(standard_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # Tombol Left to Right
        ltr_button = wx.Button(panel, label=_("Left to Right"))
        ltr_button.Bind(wx.EVT_BUTTON, self.set_left_to_right_mode)
        leftSizer.Add(ltr_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # Tombol scientific 
        scientific_button = wx.Button(panel, label=_("Scientific"))
        scientific_button.Bind(wx.EVT_BUTTON, self.ScientificMode)
        leftSizer.Add(scientific_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # Tombol conversion
        conversion_button = wx.Button(panel, label=_("Conversion"))
        conversion_button.Bind(wx.EVT_BUTTON, self.ConversionMode)  
        leftSizer.Add(conversion_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # Tombol Help
        help_button = wx.Button(panel, label=_("Help"))
        help_button.Bind(wx.EVT_BUTTON, self.show_help)
        leftSizer.Add(help_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # Panel kanan untuk riwayat
        rightSizer = wx.BoxSizer(wx.VERTICAL)
        rightSizer.Add(wx.StaticText(panel, label=_("History")), 0, wx.ALL, 5)
        self.historyBox = wx.TextCtrl(
            panel, size=(350, 300), style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_READONLY
        )
        self.historyBox.SetBackgroundColour("#f7f7f7")
        self.historyBox.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        rightSizer.Add(self.historyBox, 1, wx.EXPAND | wx.ALL, 5)

        # Gabungkan panel kiri dan kanan
        mainSizer.Add(leftSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(rightSizer, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(mainSizer)

        # Bind event untuk Escape
        self.Bind(wx.EVT_CHAR_HOOK, self.close)

        # Fokus ke input saat dialog muncul
        self.Bind(wx.EVT_SHOW, self.fokus)
        self.Show()


    def ConversionMode(self, event):
        """Membuka dialog mode conversion."""
        dialog_conversion = DialogConversion(self)  # Buat instance dari dialogConversion dengan parent
        dialog_conversion.ShowModal()       # Tampilkan dialog secara modal
        dialog_conversion.Destroy()         # Hancurkan dialog setelah ditutup


    def ScientificMode(self, event):
        """Membuka dialog mode ilmiah sin."""
        dialog_scientific = DialogScientific(self)  # Buat instance dari dialogSin dengan parent
        dialog_scientific.ShowModal()       # Tampilkan dialog secara modal
        dialog_scientific.Destroy()         # Hancurkan dialog setelah ditutup


    def fokus(self, event):
        self.number1.SetFocus()

    def close(self, event):
        k = event.GetKeyCode()
        if k == wx.WXK_ESCAPE:
            self.Destroy()
        else:
            event.Skip()

        #Mengatur mode perhitungan ke Standar Internasional.
    def set_standard_mode(self, event):
        self.calculationMode = "standard"
        ui.message(_("Calculation mode set to Standard International"))
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

        #Mengatur mode perhitungan ke Left to Right.
    def set_left_to_right_mode(self, event):
        self.calculationMode = "left_to_right"
        ui.message(_("Calculation mode set to Left to Right"))
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

        #Menampilkan pesan bantuan.
    def show_help(self, event):
        help.show_calculator_help()
        
        #Fungsi untuk menyalin hasil ke clipboard
    def salin(self, event):
        if self.re.GetValue():
            clipboard = wx.Clipboard.Get()
            if clipboard.Open():
                clipboard.SetData(wx.TextDataObject(self.re.GetValue()))
                clipboard.Close()
                ui.message(_("Result copied to clipboard"))
            else:
                ui.message(_("Failed to access clipboard"))
        else:
            ui.message(_("No result to copy"))

        #Menangani input tombol tanpa memicu hasil.
    def onKeyPressed(self, event):
        keycode = event.GetKeyCode()        
        if keycode == wx.WXK_RETURN or keycode == wx.WXK_NUMPAD_ENTER:
            # Pindahkan fokus ke kotak hasil
            self.re.SetFocus()  # Fokuskan ke kotak hasil ketika Enter ditekan
            event.Skip()  # Biarkan event diproses default
        else:
            event.Skip()  # Biarkan event lain diproses default

        #Menangani perubahan teks di kotak input
    def onTextChanged(self, event):
        expression = self.number1.GetValue().strip()
        
        if not expression:
            self.re.SetValue("")  # Kosongkan kotak hasil jika input kosong
        else:
            tones.beep(750, 50)  # Memutar nada beep saat ada input

            # Validasi input untuk hanya mengizinkan angka dan simbol matematika
            if not all(char.isdigit() or char in "+-*/().xX: " for char in expression):
                ui.message(_("Invalid input, only numbers and arithmetic symbols allowed"))
                tones.beep(440, 200)
                self.number1.SetValue(expression[:-1])  # Hapus karakter tidak valid terakhir
                self.number1.SetInsertionPointEnd()  # Set cursor ke akhir teks
            else:
                # Jalankan perhitungan real-time
                self.hitung(expression)
        event.Skip()

        #Perhitungan real-time berdasarkan mode yang dipilih
    def hitung(self, expression):
        if not expression:
            return

        self.re.SetValue("")  # Kosongkan hasil sebelum perhitungan
        expression = re.sub(r"[xX]", "*", expression).replace(":", "/")

        # Validasi simbol dan karakter
        if not re.match(r'^[0-9+\-*/(). ]+$', expression):
            self.re.SetValue(_("Error! Check Input"))
            tones.beep(440, 300)
            return

        try:
            # Hitung berdasarkan mode
            if self.calculationMode == "standard":
                result = eval(expression)
            elif self.calculationMode == "left_to_right":
                result = self.calculate_left_to_right(expression)
            else:
                ui.message(_("Invalid calculation mode"))
                return

            # Tampilkan hasil
            result = int(result) if isinstance(result, float) and result.is_integer() else result
            self.re.SetValue(str(result))

            # Perbarui riwayat
            self.history.insert(0, f"{expression} = {result}")
            self.updateHistoryBox()
        except (SyntaxError, ZeroDivisionError, ValueError):
            self.re.SetValue(_("Error! Check Input"))

        #Fungsi Menghitung ekspresi dari kiri ke kanan
    def calculate_left_to_right(self, expression):
        # Memastikan angka negatif di awal atau setelah operator diinterpretasikan dengan benar
        tokens = re.findall(r'(?<!\d)-?\d+(?:\.\d+)?|[+\-*/]', expression.replace(' ', ''))

        if not tokens:  # Jika tidak ada token, kembalikan 0
            return 0

        # Konversi token awal ke angka untuk memulai perhitungan
        result = float(tokens[0])
        i = 1

        # Iterasi melalui token
        while i < len(tokens) - 1:
            operator = tokens[i]
            next_number = float(tokens[i + 1])

            # Lakukan operasi sesuai dengan operator yang ditemukan
            if operator == '+':
                result += next_number
            elif operator == '-':
                result -= next_number
            elif operator == '*':
                result *= next_number
            elif operator == '/':
                if next_number == 0:
                    raise ZeroDivisionError("Tidak dapat membagi dengan nol.")
                result /= next_number

            i += 2  # Melompat ke operator dan angka berikutnya

        return result

    def updateHistoryBox(self):
        #Perbarui tampilan riwayat di kotak riwayat.
        self.historyBox.Value = "\n".join(self.history)  # Tampilkan seluruh riwayat


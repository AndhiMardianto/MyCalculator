# NVDA Addon: My Calculator 
# Released under the GNU General Public License v2 
# Copyright (C) 2024 - 2025 Andhi Mardianto

import globalPluginHandler
import ui

import re
import math
from decimal import Decimal, getcontext
import api
import tones
import addonHandler
import wx
import gui
from keyboardHandler import KeyboardInputGesture
from scriptHandler import script
addonHandler.initTranslation()

class DialogScientific(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Scientific Calculation", size=(800, 400))

        # Variabel untuk menyimpan riwayat
        self.history = []
        self.calculationMode = None  # Tidak ada mode perhitungan saat pertama kali

        # Panel utama untuk elemen dialog
        panel = wx.Panel(self)

        # Layout komponen di dalam dialog
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Panel kiri untuk input dan hasil
        leftSizer = wx.BoxSizer(wx.VERTICAL)

# Label input yang dapat diubah
        self.inputLabel = wx.StaticText(panel, label=_("Please Select Scientific Mode "))
        leftSizer.Add(self.inputLabel, 0, wx.ALL, 5)

        # Kotak input
        self.number1 = wx.TextCtrl(panel, size=(350, 25))
        self.number1.SetBackgroundColour("#f0f8ff")
        self.number1.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.number1.Bind(wx.EVT_CHAR_HOOK, self.onKeyPressed)
        self.number1.Bind(wx.EVT_TEXT, self.onTextChanged)
        leftSizer.Add(self.number1, 0, wx.EXPAND | wx.ALL, 5)

        # Label dan input untuk menampilkan hasil
        leftSizer.Add(wx.StaticText(panel, label=_("Result")), 0, wx.ALL, 5)
        self.re = wx.TextCtrl(panel, size=(350, 100), style=wx.TE_MULTILINE | wx.HSCROLL)
        self.re.SetBackgroundColour("#e6ffe6")
        self.re.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.re.SetEditable(False)  # Membuat teks tidak bisa diubah tanpa label "read-only"
        leftSizer.Add(self.re, 1, wx.EXPAND | wx.ALL, 5)

        # Tombol Copy
        copy_button = wx.Button(panel, label=_("Copy"))
        copy_button.Bind(wx.EVT_BUTTON, self.periksa)
        leftSizer.Add(copy_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # Tombol untuk memilih mode perhitungan
        self.sin_button = wx.Button(panel, label=_("Sin"))
        self.sin_button.Bind(wx.EVT_BUTTON, self.set_sin_mode)
        leftSizer.Add(self.sin_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        cos_button = wx.Button(panel, label=_("Cos"))
        cos_button.Bind(wx.EVT_BUTTON, self.set_cos_mode)
        leftSizer.Add(cos_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        log_button = wx.Button(panel, label=_("Log"))
        log_button.Bind(wx.EVT_BUTTON, self.show_logaritma_options)
        leftSizer.Add(log_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # Tombol untuk menghitung akar kuadrat
        sqrt_button = wx.Button(panel, label=_("Sqrt"))
        sqrt_button.Bind(wx.EVT_BUTTON, self.set_sqrt_mode)
        leftSizer.Add(sqrt_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

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

    def show_logaritma_options(self, event):
        dialog = wx.SingleChoiceDialog(
            self,
            "Select a Basis",
            "Basis Options",
            ["Natural Basis", "Base 10"]
        )
        pilihan = None
        if dialog.ShowModal() == wx.ID_OK:
            pilihan = dialog.GetStringSelection()
        
        dialog.Destroy()  # Pastikan dialog ditutup setelah dipilih

        if pilihan == "Natural Basis":
            self.set_log_basis_natural(None)
        elif pilihan == "Base 10":
            self.set_log_basis_10(None)



    def set_sin_mode(self, event):
        """Set mode perhitungan ke Sin."""
        self.calculationMode = "sin"
        self.inputLabel.SetLabel(_("Input in Degrees:"))  # Perbarui label input
        ui.message(_("Calculation mode set to Sin"))
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def set_cos_mode(self, event):
        """Set mode perhitungan ke Cos."""
        self.calculationMode = "cos"
        self.inputLabel.SetLabel(_("Input in Degrees:"))  # Perbarui label input
        ui.message(_("Calculation mode set to Cos"))
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def set_log_basis_natural(self, event):
        """Set mode perhitungan ke Log."""
        self.calculationMode = "LogBasisNatural"
        self.inputLabel.SetLabel(_("Input in Basis Natural :"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def set_log_basis_10(self, event):
        #Set mode perhitungan ke basis 10
        self.calculationMode = "Basis10"
        self.inputLabel.SetLabel(_("Input in Basis 10:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def set_sqrt_mode(self, event):
        """Set mode perhitungan ke Sqrt (Akar Kuadrat)."""
        self.calculationMode = "sqrt"
        self.inputLabel.SetLabel(_("Input in Non-Negative Numbers:"))  # Perbarui label input
        ui.message(_("Calculation mode set to Sqrt"))
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input


    def periksa(self, event):
        """Fungsi untuk menyalin hasil ke clipboard."""
        if self.re.GetValue():
            # Salin hasil ke clipboard
            clipboard = wx.Clipboard.Get()
            if clipboard.Open():
                clipboard.SetData(wx.TextDataObject(self.re.GetValue()))
                clipboard.Close()
                ui.message(_("Result copied to clipboard"))
            else:
                ui.message(_("Failed to access clipboard"))
        else:
            ui.message(_("No result to copy"))

    def hitung(self, expression):
        if self.calculationMode is None:
            ui.message(_("Please select a calculation mode first"))
            tones.beep(440, 300)
            return

        if not expression:
            return

        self.re.SetValue("")  # Kosongkan hasil sebelum perhitungan
        expression = re.sub(r"[xX]", "*", expression).replace(":", "/")

        try:
            # Validasi dan hitung berdasarkan mode
            value = float(expression)
            getcontext().prec = 50  # Set presisi tinggi untuk perhitungan internal

            if self.calculationMode == "sin":
                value_decimal = Decimal(math.radians(value))
                result = Decimal(math.sin(float(value_decimal)))
            elif self.calculationMode == "cos":
                value_decimal = Decimal(math.radians(value))
                result = Decimal(math.cos(float(value_decimal)))
            elif self.calculationMode == "LogBasisNatural":
                if value <= 0:
                    ui.message(_("Logarithm is only defined for positive numbers"))
                    tones.beep(440, 100)
                    return
                result = Decimal(value).ln()
            elif self.calculationMode == "Basis10":
                if value <= 0:
                    ui.message(_("Logarithm is only defined for positive numbers"))
                    tones.beep(440, 100)
                    return
                result = Decimal(value).log10()
            elif self.calculationMode == "sqrt":
                if value < 0:
                    ui.message(_("Square root is only defined for non-negative numbers"))
                    tones.beep(440, 100)
                    return
                result = Decimal(value).sqrt()
            else:
                result = Decimal(eval(expression))

            # Jika hasil mendekati nol, set ke 0
            if abs(result) < Decimal('1e-10'):
                result = Decimal(0)

            # Tampilkan hasil dengan presisi tinggi dan pembulatan
            precision = 2  # Jumlah desimal untuk pembulatan
            rounded_result = round(result, precision)

            # Format hasil untuk kotak output
            output = (
                _("High Precision = {result}\nRounded = {rounded_result}")
            ).format(result=result, precision=precision, rounded_result=rounded_result)
            self.re.SetValue(output)

            # Simpan riwayat hanya dengan pembulatan
            self.history.insert(0, f"{expression} = {rounded_result}")
            self.updateHistoryBox()

        except ValueError:
            ui.message(_("Invalid input. Please check your expression"))
        except Exception as e:
            ui.message(_("An error occurred: ") + str(e))

    def onTextChanged(self, event):
        #Menangani perubahan teks di kotak input.
        expression = self.number1.GetValue().strip()
        if not expression:
            self.re.SetValue("")  # Kosongkan kotak hasil jika input kosong
        else:
            tones.beep(750, 50)  # Memutar nada beep saat ada input

            # Validasi input untuk hanya mengizinkan angka dan simbol matematika
            if not all(char.isdigit() or char in "-. " for char in expression):            
                ui.message(_("Invalid input, only numbers allowed"))
                tones.beep(440, 100)
                self.number1.SetValue(expression[:-1])  # Hapus karakter tidak valid terakhir
                self.number1.SetInsertionPointEnd()  # Set cursor ke akhir teks
            elif self.calculationMode:  # Pastikan mode sudah dipilih
                self.hitung(expression)  # Lakukan perhitungan real-time
        event.Skip()


    def fokus(self, event):
        """Fokuskan kotak input ketika dialog ditampilkan."""
        self.sin_button.SetFocus()

    def close(self, event):
        """Menangani penutupan dialog saat tombol Escape ditekan."""
        k = event.GetKeyCode()
        if k == wx.WXK_ESCAPE:
            self.Destroy()  # Tutup dialog jika Escape ditekan
        else:
            event.Skip()

    def onKeyPressed(self, event):
        """Menangani input tombol tanpa memicu hasil."""
        keycode = event.GetKeyCode()        
        if keycode == wx.WXK_RETURN or keycode == wx.WXK_NUMPAD_ENTER:
            # Pindahkan fokus ke kotak hasil
            self.re.SetFocus()  # Fokuskan ke kotak hasil ketika Enter ditekan
            event.Skip()  # Biarkan event diproses default
        else:
            event.Skip()  # Biarkan event lain diproses default

    def updateHistoryBox(self):
        """Perbarui tampilan riwayat di kotak riwayat."""
        self.historyBox.Value = "\n".join(self.history)  # Tampilkan seluruh riwayat

    

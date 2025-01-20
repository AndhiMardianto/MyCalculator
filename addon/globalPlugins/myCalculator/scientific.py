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

        # Variabel untuk menyimpan riwayat dan mode
        self.history = []
        self.calculationMode = None  # Tidak ada mode perhitungan saat pertama kali
        self.isRadian = False  # Default mode adalah derajat

        # Panel utama untuk elemen dialog
        panel = wx.Panel(self)

        # Layout komponen di dalam dialog
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Panel kiri untuk input dan hasil
        leftSizer = wx.BoxSizer(wx.VERTICAL)

        # Checkbox untuk memilih input dalam derajat atau radian
        self.radianCheckbox = wx.CheckBox(panel, label=_("Use Radians"))
        self.radianCheckbox.Bind(wx.EVT_CHECKBOX, self.toggleInputMode)
        leftSizer.Add(self.radianCheckbox, 0, wx.ALL, 5)


        # Label input
        self.inputLabel = wx.StaticText(panel, label=_("Please Select Scientific Mode"))
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
        self.re.SetEditable(False)  # Membuat teks tidak bisa diubah
        leftSizer.Add(self.re, 1, wx.EXPAND | wx.ALL, 5)

        # Tombol Copy
        copy_button = wx.Button(panel, label=_("Copy"))
        copy_button.Bind(wx.EVT_BUTTON, self.periksa)
        leftSizer.Add(copy_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # Tombol untuk memilih mode perhitungan
        buttons = [
            (_("Sin"), self.set_sin_mode),
            (_("Asin"), self.set_asin_mode),
            (_("Cos"), self.set_cos_mode),
            (_("Acos"), self.set_acos_mode),
            (_("Tan"), self.set_tan_mode),
            (_("Atan"), self.set_atan_mode),
            (_("Log"), self.show_logaritma_options),
            (_("Sqrt"), self.set_sqrt_mode),
        ]

        for label, handler in buttons:
            button = wx.Button(panel, label=label)
            button.Bind(wx.EVT_BUTTON, handler)
            leftSizer.Add(button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

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

        #Mengubah mode input antara derajat dan radian.
    def toggleInputMode(self, event):
        self.isRadian = self.radianCheckbox.IsChecked()
        mode = _("Radian") if self.isRadian else _("Degree")        
        # Panggil fungsi untuk menerapkan perubahan mode
        self.refreshMode()
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def refreshMode(self):
        """Memeriksa mode saat ini dan merefresh ulang perhitungannya."""
        if self.calculationMode:
            # Panggil ulang fungsi sesuai dengan mode yang sedang aktif
            if self.calculationMode == "sin":
                self.set_sin_mode(None)
            elif self.calculationMode == "cos":
                self.set_cos_mode(None)
            elif self.calculationMode == "tan":
                self.set_tan_mode(None)
            elif self.calculationMode == "asin":
                self.set_asin_mode(None)
            elif self.calculationMode == "acos":
                self.set_acos_mode(None)
            elif self.calculationMode == "atan":
                self.set_atan_mode(None)


    def show_logaritma_options(self, event):
        dialog = wx.SingleChoiceDialog(
            self,
            _("Select a Basis"),
            _("Basis Options"),
            [_("Natural Base"), _("Base 10")]
        )
        pilihan = None
        if dialog.ShowModal() == wx.ID_OK:
            pilihan = dialog.GetStringSelection()
        
        dialog.Destroy()  # Pastikan dialog ditutup setelah dipilih

        if pilihan == _("Natural Base"):
            self.set_log_basis_natural(None)
        elif pilihan == _("Base 10"):
            self.set_log_basis_10(None)

    def set_sin_mode(self, event):
        """Set mode perhitungan ke Sin."""
        self.calculationMode = "sin"
        input_mode = _("Radians") if self.isRadian else _("Degrees")  # Tentukan mode input
        self.inputLabel.SetLabel(f"Input in {input_mode}:")  # Perbarui label input
        ui.message(_("Calculation mode set to Sin (Input in ") + input_mode + ")")
        
        # Ambil nilai ekspresi dari kotak input dan lakukan perhitungan
        expression = self.number1.GetValue().strip()
        self.hitung(expression)  
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def set_cos_mode(self, event):
        """Set mode perhitungan ke Cos."""
        self.calculationMode = "cos"
        input_mode = _("Radians") if self.isRadian else _("Degrees")  # Tentukan mode input
        self.inputLabel.SetLabel(f"Input in {input_mode}:")  # Perbarui label input
        ui.message(_("Calculation mode set to Cos (Input in ") + input_mode + ")")
        
        # Ambil nilai ekspresi dari kotak input dan lakukan perhitungan
        expression = self.number1.GetValue().strip()
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

    def set_asin_mode(self, event):
        """Set mode perhitungan ke Asin (Arcsin)."""
        self.calculationMode = "asin"
        mode = _("Radians") if self.isRadian else _("Degrees")
        self.inputLabel.SetLabel(_(f"Input in Range [-1, 1] ({mode}):"))  # Perbarui label input
        ui.message(_("Calculation mode set to Asin"))
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def set_acos_mode(self, event):
        """Set mode perhitungan ke Acos (Arccos)."""
        self.calculationMode = "acos"
        mode = _("Radians") if self.isRadian else _("Degrees")
        self.inputLabel.SetLabel(_(f"Input in Range [-1, 1] ({mode}):"))  # Perbarui label input
        ui.message(_("Calculation mode set to Acos"))
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def set_tan_mode(self, event):
        """Set mode perhitungan ke Tan (Tangen)."""
        self.calculationMode = "tan"
        mode = _("Radians") if self.isRadian else _("Degrees")
        self.inputLabel.SetLabel(_(f"Input in {mode}:"))  # Perbarui label input
        ui.message(_("Calculation mode set to Tan"))
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def set_atan_mode(self, event):
        """Set mode perhitungan ke Atan (Arctangen)."""
        self.calculationMode = "atan"
        mode = _("Radians") if self.isRadian else _("Degrees")
        self.inputLabel.SetLabel(_(f"Input in Any Real Number ({mode}):"))  # Perbarui label input
        ui.message(_("Calculation mode set to Atan"))
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
        """Perform the calculation."""
        if self.calculationMode is None:
            ui.message(_("Please select a calculation mode first"))
            tones.beep(440, 300)
            return

        if not expression:
            return

        self.re.SetValue("")  # Clear result before calculation
        expression = re.sub(r"[xX]", "*", expression).replace(":", "/")

        try:
            value = float(expression)
            getcontext().prec = 50  # Set high precision for calculations

            if self.calculationMode in ["sin", "cos", "tan"]:
                if not self.isRadian:
                    # Konversi derajat ke radian jika mode input adalah derajat
                    value = math.radians(value)

                if self.calculationMode == "sin":
                    result = Decimal(math.sin(value))
                elif self.calculationMode == "cos":
                    result = Decimal(math.cos(value))
                elif self.calculationMode == "tan":
                    result = Decimal(math.tan(value))

            elif self.calculationMode in ["asin", "acos", "atan"]:
                if self.calculationMode == "asin":
                    if value < -1 or value > 1:
                        ui.message(_("Arcsine is only defined for values between -1 and 1"))
                        tones.beep(440, 100)
                        return
                    result = math.asin(value)
                elif self.calculationMode == "acos":
                    if value < -1 or value > 1:
                        ui.message(_("Arccosine is only defined for values between -1 and 1"))
                        tones.beep(440, 100)
                        return
                    result = math.acos(value)
                elif self.calculationMode == "atan":
                    result = math.atan(value)

                # Konversi hasil ke derajat jika mode input bukan radian
                if not self.isRadian:
                    result = math.degrees(result)
                result = Decimal(result)

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

            # Periksa apakah hasil sangat kecil dan anggap sebagai nol
            if abs(result) < Decimal('1e-10'):
                result = Decimal(0)

            # Tentukan presisi pembulatan
            precision = 2
            rounded_result = result.quantize(Decimal(f'1.{"0" * precision}'))

            # Format output
            output = (
                _("High Precision = {result}\nRounded = {rounded_result}")
            ).format(result=result, rounded_result=rounded_result)
            self.re.SetValue(output)

            # Tambahkan ke riwayat
            self.history.insert(0, f"{expression} = {rounded_result}")
            self.updateHistoryBox()

        except ValueError:
            ui.message(_("Invalid input. Please check your expression"))
        except Exception as e:
            ui.message(_("An error occurred: ") + str(e))


    def onTextChanged(self, event):
        # Menangani perubahan teks di kotak input.
        expression = self.number1.GetValue().strip()
        if not expression:
            self.re.SetValue("")  # Kosongkan kotak hasil jika input kosong
        else:
            tones.beep(750, 50)  # Memutar nada beep saat ada input

            # Validasi input yang lebih spesifik
            valid_pattern = r"^-?\d*(\.\d*)?$"  # Angka negatif atau positif, opsional desimal
            if not re.match(valid_pattern, expression):
                ui.message(_("Invalid input, only valid numbers are allowed"))
                tones.beep(440, 100)
                self.number1.SetValue(expression[:-1])  # Hapus karakter tidak valid terakhir
                self.number1.SetInsertionPointEnd()  # Set cursor ke akhir teks
            elif self.calculationMode and expression not in "-.":  # Pastikan input bukan hanya tanda saja
                self.hitung(expression)  # Lakukan perhitungan real-time
        event.Skip()


    def fokus(self, event):
        """Fokuskan kotak input ketika dialog ditampilkan."""
        #self.sin_button.SetFocus()

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

    

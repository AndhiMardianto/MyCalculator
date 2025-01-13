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
from keyboardHandler import KeyboardInputGesture
from scriptHandler import script
addonHandler.initTranslation()

class DialogConversion(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Conversion", size=(800, 400))

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
        self.inputLabel = wx.StaticText(panel, label=_("Please Select Conversion Mode"))
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
        self.re = wx.TextCtrl(panel, size=(350, 100), style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_READONLY)
        self.re.SetBackgroundColour("#e6ffe6")
        self.re.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        leftSizer.Add(self.re, 1, wx.EXPAND | wx.ALL, 5)

        # Tombol Copy
        copy_button = wx.Button(panel, label=_("Copy"))
        copy_button.Bind(wx.EVT_BUTTON, self.periksa)
        leftSizer.Add(copy_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # Tombol untuk memilih mode perhitungan
        self.length_button = wx.Button(panel, label=_("Length"))
        self.length_button.Bind(wx.EVT_BUTTON, self.show_length_options)
        leftSizer.Add(self.length_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        mass_button = wx.Button(panel, label=_("Mass"))
        mass_button.Bind(wx.EVT_BUTTON, self.show_mass_options)
        leftSizer.Add(mass_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        temperature_button = wx.Button(panel, label=_("Temperature"))
        temperature_button.Bind(wx.EVT_BUTTON, self.show_temperature_options)
        leftSizer.Add(temperature_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        volume_button = wx.Button(panel, label=_("Volume"))
        volume_button.Bind(wx.EVT_BUTTON, self.show_volume_options)
        leftSizer.Add(volume_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # Tombol untuk memilih mode konversi Kecepatan (Speed)
        speed_button = wx.Button(panel, label=_("Speed"))
        speed_button.Bind(wx.EVT_BUTTON, self.show_speed_options)
        leftSizer.Add(speed_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

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

        self.Bind(wx.EVT_SHOW, self.fokus)

        self.Show()

    # Fungsi untuk menunjukkan opsi kecepatan
    def show_speed_options(self, event):
        dialog = wx.SingleChoiceDialog(
            self,
            _("Select a Speed conversion:"),
            _("Speed Conversion Options"),
            [
                "Kilometers per Hour to Miles per Hour",
                "Miles per Hour to Kilometers per Hour",
                "Meters per Second to Kilometers per Hour",
                "Kilometers per Hour to Meters per Second",
                "Meters per Second to Miles per Hour",
                "Miles per Hour to Meters per Second",
                "Knots to Kilometers per Hour",
                "Kilometers per Hour to Knots",
                "Knots to Miles per Hour",
                "Miles per Hour to Knots",
                "Feet per Second to Kilometers per Hour",
                "Kilometers per Hour to Feet per Second",
            ]
        )
        pilihan = None
        if dialog.ShowModal() == wx.ID_OK:
            pilihan = dialog.GetStringSelection()
        if pilihan == "Kilometers per Hour to Miles per Hour":
            self.kmh_to_mph(None)
        elif pilihan == "Miles per Hour to Kilometers per Hour":
            self.mph_to_kmh(None)
        elif pilihan == "Meters per Second to Kilometers per Hour":
            self.ms_to_kmh(None)
        elif pilihan == "Kilometers per Hour to Meters per Second":
            self.kmh_to_ms(None)
        elif pilihan == "Meters per Second to Miles per Hour":
            self.ms_to_mph(None)
        elif pilihan == "Miles per Hour to Meters per Second":
            self.mph_to_ms(None)
        elif pilihan == "Knots to Kilometers per Hour":
            self.knot_to_kmh(None)
        elif pilihan == "Kilometers per Hour to Knots":
            self.kmh_to_knot(None)
        elif pilihan == "Knots to Miles per Hour":
            self.knot_to_mph(None)
        elif pilihan == "Miles per Hour to Knots":
            self.mph_to_knot(None)
        elif pilihan == "Feet per Second to Kilometers per Hour":
            self.fps_to_kmh(None)
        elif pilihan == "Kilometers per Hour to Feet per Second":
            self.kmh_to_fps(None)

        dialog.Destroy()

    def kmh_to_mph(self, event):
        self.calculationMode = "KmhToMph"
        self.inputLabel.SetLabel(_("Input in Kilometers per Hour:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def mph_to_kmh(self, event):
        self.calculationMode = "MphToKmh"
        self.inputLabel.SetLabel(_("Input in Miles per Hour:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def ms_to_kmh(self, event):
        self.calculationMode = "MsToKmh"
        self.inputLabel.SetLabel(_("Input in Meters per Second:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def kmh_to_ms(self, event):
        self.calculationMode = "KmhToMs"
        self.inputLabel.SetLabel(_("Input in Kilometers per Hour:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def ms_to_mph(self, event):
        self.calculationMode = "MsToMph"
        self.inputLabel.SetLabel(_("Input in Meters per Second:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def mph_to_ms(self, event):
        self.calculationMode = "MphToMs"
        self.inputLabel.SetLabel(_("Input in Miles per Hour:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def knot_to_kmh(self, event):
        self.calculationMode = "KnotToKmh"
        self.inputLabel.SetLabel(_("Input in Knots:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def kmh_to_knot(self, event):
        self.calculationMode = "KmhToKnot"
        self.inputLabel.SetLabel(_("Input in Kilometers per Hour:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def knot_to_mph(self, event):
        self.calculationMode = "KnotToMph"
        self.inputLabel.SetLabel(_("Input in Knots:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def mph_to_knot(self, event):
        self.calculationMode = "MphToKnot"
        self.inputLabel.SetLabel(_("Input in Miles per Hour:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def fps_to_kmh(self, event):
        self.calculationMode = "FpsToKmh"
        self.inputLabel.SetLabel(_("Input in Feet per Second:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def kmh_to_fps(self, event):
        self.calculationMode = "KmhToFps"
        self.inputLabel.SetLabel(_("Input in Kilometers per Hour:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input









    def show_length_options(self, event):
        """Menampilkan opsi konversi panjang/jarak."""
        # Tampilkan opsi konversi panjang/jarak
        dialog = wx.SingleChoiceDialog(
            self,
            _("Select a length conversion:"),
            _("Length Conversion Options"),
            ["Kilometers to Miles", "Miles to Kilometers", "Meters to Feet", "Feet to Meters", "Centimeters to Inches", "Inches to Centimeters"]
        )
        pilihan = None
        if dialog.ShowModal() == wx.ID_OK:
            pilihan = dialog.GetStringSelection()

        if pilihan == "Kilometers to Miles":
            self.KmToMiles(None)  # Panggil fungsi konversi Kilometers ke Miles
        elif pilihan== "Miles to Kilometers":
            self.MilestoKm(None)
        elif pilihan== "Meters to Feet":
            self.MetersToFeet(None)
        elif pilihan == "Feet to Meters":
            self.FeetToMeters(None)
        elif pilihan == "Centimeters to Inches":
                    self.CmToInches(None)
        elif pilihan == "Inches to Centimeters":
            self.InchesToCm(None)
            dialog.Destroy()



    def KmToMiles(self, event):
        self.calculationMode = "Kilometers to Miles"
        self.inputLabel.SetLabel(_("Input in Kilometers:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def MilestoKm(self, event):
        self.calculationMode = "Miles to Kilometers"
        self.inputLabel.SetLabel(_("Input in Miles:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def MetersToFeet(self, event):
        self.calculationMode = "meters to feet"
        self.inputLabel.SetLabel(_("Input in Meters:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def FeetToMeters(self, event):
        self.calculationMode = "feet to meters"
        self.inputLabel.SetLabel(_("Input in Feet:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def CmToInches(self, event):
        self.calculationMode = "centimeters to inches"
        self.inputLabel.SetLabel(_("Input in Centimeters:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def InchesToCm(self, event):
        self.calculationMode = "inches to centimeters"
        self.inputLabel.SetLabel(_("Input in Inches:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input


# popup massa 
    def show_mass_options(self, event):
        dialog = wx.SingleChoiceDialog(
            self,
            _("Select a Mass conversion:"),
            _("Mass Conversion Options"),
            ["Kilograms to Pounds", "Pounds to Kilograms", "Tons to Kilograms", "Kilograms to Tons", "Ounces to Grams", "Grams to Ounces"]
        )
        pilihan = None
        if dialog.ShowModal() == wx.ID_OK:
            pilihan = dialog.GetStringSelection()

        if pilihan == "Kilograms to Pounds":
            self.KgToPounds(None)  
        elif pilihan== "Pounds to Kilograms":
            self.PoundsToKg(None)
        elif pilihan== "Tons to Kilograms":
            self.TonsToKg(None)
        elif pilihan == "Kilograms to Tons":
            self.KgToTons(None)
        elif pilihan == "Ounces to Grams":
                    self.Ounces_To_Grams(None)
        elif pilihan == "Grams to Ounces":
            self.GramsToOunces(None)
            dialog.Destroy()

    def KgToPounds(self, event):
        self.calculationMode = "Kilograms to Pounds"
        self.inputLabel.SetLabel(_("Input in Kilograms:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def PoundsToKg(self, event):
        self.calculationMode = "Pounds to Kilograms"
        self.inputLabel.SetLabel(_("Input in Pounds:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def TonsToKg(self, event):
        self.calculationMode = "Tons to Kilograms"
        self.inputLabel.SetLabel(_("Input in Tons:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)
        self.number1.SetFocus()

    def KgToTons(self, event):
        self.calculationMode = "Kilograms to Tons"
        self.inputLabel.SetLabel(_("Input in Kilograms:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)
        self.number1.SetFocus()

    def Ounces_To_Grams(self, event):
        self.calculationMode = "Ounces to Grams"
        self.inputLabel.SetLabel(_("Input in Ounces:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)
        self.number1.SetFocus()

    def GramsToOunces(self, event):
        self.calculationMode = "Grams to Ounces"
        self.inputLabel.SetLabel(_("Input in Grams:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)
        self.number1.SetFocus()

# popup temperature 
    def show_temperature_options(self, event):
        dialog = wx.SingleChoiceDialog(
            self,
            _("Select a Temperature conversion:"),
            _("Temperature Conversion Options"),
            ["Celsius to Fahrenheit", "Fahrenheit to Celsius", "Celsius to Kelvin", "Kelvin to Celsius", "Fahrenheit to Kelvin", "Kelvin to Fahrenheit"]
        )
        pilihan = None
        if dialog.ShowModal() == wx.ID_OK:
            pilihan = dialog.GetStringSelection()

        if pilihan == "Celsius to Fahrenheit":
            self.c_to_f(None)  
        elif pilihan== "Fahrenheit to Celsius":
            self.f_to_c(None)
        elif pilihan== "Celsius to Kelvin":
            self.c_to_k(None)
        elif pilihan == "Kelvin to Celsius":
            self.k_to_c(None)
        elif pilihan == "Fahrenheit to Kelvin":
                    self.f_to_k(None)
        elif pilihan == "Kelvin to Fahrenheit":
            self.k_to_f(None)
            dialog.Destroy()

    def c_to_f(self, event):
        self.calculationMode = "C_to_F"
        self.inputLabel.SetLabel(_("Input in Celsius:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def f_to_c(self, event):
        self.calculationMode = "F_to_C"
        self.inputLabel.SetLabel(_("Input in Fahrenheit:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def c_to_k(self, event):
        self.calculationMode = "C_to_K"
        self.inputLabel.SetLabel(_("Input in Celsius:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def k_to_c(self, event):
        self.calculationMode = "K_to_C"
        self.inputLabel.SetLabel(_("Input in Kelvin:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def  f_to_k(self, event):
        self.calculationMode = "F_to_K"
        self.inputLabel.SetLabel(_("Input in Fahrenheit:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def k_to_f(self, event):
        self.calculationMode = "K_to_F"
        self.inputLabel.SetLabel(_("Input in Kelvin:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

# popup volume 

    def show_volume_options(self, event):
        dialog = wx.SingleChoiceDialog(
            self,
            _("Select a Volume conversion:"),
            _("Volume Conversion Options"),
            [
                "Liter to Gallon (US)",
                "Gallon (US) to Liter",
                "Liter to Milliliter",
                "Milliliter to Liter",
                "Cubic Meter to Liter",
                "Liter to Cubic Meter",
                "Gallon (UK) to Liter",
                "Liter to Gallon (UK)",
                "Cubic Inch to Liter",
                "Liter to Cubic Inch",
                "Milliliter to Cubic Centimeter",
                "Cubic Centimeter to Milliliter",
                "Barrel (US) to Liter",
                "Liter to Barrel (US)"
            ]
        )
        pilihan = None
        if dialog.ShowModal() == wx.ID_OK:
            pilihan = dialog.GetStringSelection()
        if pilihan == "Liter to Gallon (US)":
            self.ltr_to_gl_us(None)  
        elif pilihan== "Gallon (US) to Liter":
            self.gl_us_to_ltr(None)
        elif pilihan == "Liter to Milliliter":
            self.lt_to_ml(None)
        elif pilihan == "Milliliter to Liter":
            self.ml_to_lt(None)
        elif pilihan == "Cubic Meter to Liter":
            self.cbcm_to_ltr(None)
        elif pilihan == "Liter to Cubic Meter":
            self.ltr_to_cbcm(None)
        elif pilihan =="Gallon (UK) to Liter":
            self.gluk_to_ltr(None)
        elif pilihan == "Liter to Gallon (UK)":
            self.ltr_to_gluk(None)
        elif pilihan == "Cubic Inch to Liter":
            self.cbcinc_to_ltr(None)
        elif pilihan == "Liter to Cubic Inch":
            self.ltr_to_cbcinc(None)
        elif pilihan =="Milliliter to Cubic Centimeter":
            self.ml_to_cbccm(None)
        elif pilihan == "Cubic Centimeter to Milliliter":
            self.cbccm_to_ml(None)
        elif pilihan == "Barrel (US) to Liter":
            self.barelus_to_ltr(None)
        elif pilihan == "Liter to Barrel (US)":
            self.ltr_to_barelus(None)

            dialog.Destroy()

    def ltr_to_gl_us(self, event):
        self.calculationMode = "LiterToGallonUs"
        self.inputLabel.SetLabel(_("Input in Liter:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def gl_us_to_ltr(self, event):
        self.calculationMode = "GallonUsToLiter"
        self.inputLabel.SetLabel(_("Input in Gallon (US):"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def lt_to_ml(self, event):
        self.calculationMode = "LtrToMl"
        self.inputLabel.SetLabel(_("Input in Liter:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def ml_to_lt(self, event):
        self.calculationMode = "MlToLtr"
        self.inputLabel.SetLabel(_("Input in Milliliter:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def cbcm_to_ltr(self, event):
        self.calculationMode = "CbcmToLtr"
        self.inputLabel.SetLabel(_("Input in Cubic Meter:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def ltr_to_cbcm(self, event):
        self.calculationMode = "LtrToCbcm"
        self.inputLabel.SetLabel(_("Input in Liter:"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def gluk_to_ltr(self, event):
        self.calculationMode = "GlUkToLtr"
        self.inputLabel.SetLabel(_("Input in Gallon (UK) :"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def ltr_to_gluk(self, event):
        self.calculationMode = "LtrToGlUk"
        self.inputLabel.SetLabel(_("Input in Liter :"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def cbcinc_to_ltr(self, event):
        self.calculationMode = "CbcincToLtr"
        self.inputLabel.SetLabel(_("Input in Cubic Inch :"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def ltr_to_cbcinc(self, event):
        self.calculationMode = "LtrToCbcinc"
        self.inputLabel.SetLabel(_("Input in Liter :"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def ml_to_cbccm(self, event):
        self.calculationMode = "MlToCbccm"
        self.inputLabel.SetLabel(_("Input in Milliliter :"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def cbccm_to_ml(self, event):
        self.calculationMode = "CbccmToMl"
        self.inputLabel.SetLabel(_("Input in Cubic Centimeter :"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def barelus_to_ltr(self, event):
        self.calculationMode = "BarelUsToLtr"
        self.inputLabel.SetLabel(_("Input in Barrel (US) :"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input

    def ltr_to_barelus(self, event):
        self.calculationMode = "LtrToBarelUs"
        self.inputLabel.SetLabel(_("Input in Liter :"))  
        expression = self.number1.GetValue().strip()  # Ambil nilai ekspresi dari kotak input
        self.hitung(expression)  # Panggil fungsi hitung dengan ekspresi
        self.number1.SetFocus()  # Pindahkan fokus ke kotak input




# fungsi hitung 
    def hitung(self, expression):
        self.re.SetValue("")  # Kosongkan hasil sebelum perhitungan
        expression = re.sub(r"[xX]", "*", expression).replace(":", "/")

        try:
            # Validasi dan hitung berdasarkan mode
            value = float(expression)  # Pastikan input adalah angka valid

            if self.calculationMode == "Kilometers to Miles":
                result = value * 0.621371  # Konversi kilometer ke miles
            elif self.calculationMode == "Miles to Kilometers":
                result = value / 0.621371  # Konversi miles ke kilometer
            elif self.calculationMode == "meters to feet":
                result = value * 3.28084  # Konversi meter ke feet
            elif self.calculationMode == "feet to meters":
                result = value / 3.28084  # Konversi feet ke meter
            elif self.calculationMode == "centimeters to inches":
                result = value / 2.54  # Konversi cm ke inch
            elif self.calculationMode == "inches to centimeters":
                result = value * 2.54  # Konversi inch ke cm
            elif self.calculationMode == "Kilograms to Pounds":
                result = value * 2.20462  # Konversi kilogram ke pound
            elif self.calculationMode == "Pounds to Kilograms":
                result = value / 2.20462  # Konversi pound ke kilogram
            elif self.calculationMode == "Tons to Kilograms":
                result = value * 1000  # Konversi ton ke kilogram
            elif self.calculationMode == "Kilograms to Tons":
                result = value / 1000  # Konversi kilogram ke ton
            elif self.calculationMode == "Ounces to Grams":
                result = value * 28.3495  # Konversi ounce ke gram
            elif self.calculationMode == "Grams to Ounces":
                result = value / 28.3495  # Konversi gram ke ounce
            elif self.calculationMode == "C_to_F":
                result = (value * 9 / 5) + 32  # Konversi Celsius ke Fahrenheit
            elif self.calculationMode == "F_to_C":
                result = (value - 32) * 5 / 9  # Konversi Fahrenheit ke Celsius
            elif self.calculationMode == "C_to_K":
                result = value + 273.15  # Konversi Celsius ke Kelvin
            elif self.calculationMode == "K_to_C":
                result = value - 273.15  # Konversi Kelvin ke Celsius
            elif self.calculationMode == "F_to_K":
                result = ((value - 32) * 5 / 9) + 273.15  # Konversi Fahrenheit ke Kelvin
            elif self.calculationMode == "K_to_F":
                result = ((value - 273.15) * 9 / 5) + 32  # Konversi Kelvin ke Fahrenheit
            elif self.calculationMode == "LiterToGallonUs":
                result = value * 0.264172  # 1 liter = 0.264172 US gallons
            elif self.calculationMode == "GallonUsToLiter":
                result = value / 0.264172  # 1 US gallon = 3.78541 liters
            elif self.calculationMode == "LtrToMl":
                result = value * 1000  # 1 liter = 1000 milliliter
            elif self.calculationMode == "MlToLtr":
                result = value / 1000  # 1 milliliter = 0.001 liter
            elif self.calculationMode == "CbcmToLtr":
                result = value * 1000  # 1 cubic meter = 1000 liters
            elif self.calculationMode == "LtrToCbcm":
                result = value / 1000  # 1 liter = 0.001 cubic meter
            elif self.calculationMode == "GlUkToLtr":
                result = value * 4.54609  # 1 UK gallon = 4.54609 liters
            elif self.calculationMode == "LtrToGlUk":
                result = value / 4.54609  # 1 liter = 0.219969 UK gallons
            elif self.calculationMode == "CbcincToLtr":
                result = value * 0.0163871  # 1 cubic inch = 0.0163871 liters
            elif self.calculationMode == "LtrToCbcinc":
                result = value / 0.0163871  # 1 liter = 61.0237 cubic inches
            elif self.calculationMode == "MlToCbccm":
                result = value  # 1 milliliter = 1 cubic centimeter
            elif self.calculationMode == "CbccmToMl":
                result = value  # 1 cubic centimeter = 1 milliliter
            elif self.calculationMode == "BarelUsToLtr":
                result = value * 119.2404717  # 1 US barrel = 119.2404717 liters
            elif self.calculationMode == "LtrToBarelUs":
                result = value / 119.2404717  # 1 liter = 0.0083864143605761 US barrels

            elif self.calculationMode == "KmhToMph":
                result = value * 0.621371  # Konversi Kilometer per Jam ke Miles per Jam
            elif self.calculationMode == "MphToKmh":
                result = value / 0.621371  # Konversi Miles per Jam ke Kilometer per Jam
            elif self.calculationMode == "MsToKmh":
                result = value * 3.6  # Konversi Meter per Detik ke Kilometer per Jam
            elif self.calculationMode == "KmhToMs":
                result = value / 3.6  # Konversi Kilometer per Jam ke Meter per Detik
            elif self.calculationMode == "MsToMph":
                result = value * 2.23694  # Konversi Meter per Detik ke Miles per Jam
            elif self.calculationMode == "MphToMs":
                result = value / 2.23694  # Konversi Miles per Jam ke Meter per Detik
            elif self.calculationMode == "KnotToKmh":
                result = value * 1.852  # Konversi Knot ke Kilometer per Jam
            elif self.calculationMode == "KmhToKnot":
                result = value / 1.852  # Konversi Kilometer per Jam ke Knot
            elif self.calculationMode == "KnotToMph":
                result = value * 1.15078  # Konversi Knot ke Miles per Jam
            elif self.calculationMode == "MphToKnot":
                result = value / 1.15078  # Konversi Miles per Jam ke Knot
            elif self.calculationMode == "FpsToKmh":
                result = value * 1.09728  # Konversi Feet per Detik ke Kilometer per Jam
            elif self.calculationMode == "KmhToFps":
                result = value / 1.09728  # Konversi Kilometer per Jam ke Feet per Detik






                
            # Tampilkan hasil
            self.re.SetValue(str(result))

            # Tambahkan hasil ke riwayat
            self.history.insert(0, f"{expression} = {result}")
            self.updateHistoryBox()

        except ValueError:
            pass
        except Exception as e:
            pass

    def periksa(self, event):
        #Fungsi untuk menyalin hasil ke clipboard.
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
        if event.Show:
            self.length_button.SetFocus()

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
        self.historyBox.Value = "\n".join(self.history)  # Tampilkan seluruh riwayat

    
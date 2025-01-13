import wx
import gui
import addonHandler
addonHandler.initTranslation()
import gui 

def show_calculator_help():
    """Menampilkan dialog penjelasan tentang mode Standard dan Left to Right dengan aksesibilitas pembaca layar."""
    
    # Dialog penjelasan tentang mode Standard
    dialog = wx.Dialog(None, title=_("Calculation Mode Help"), size=(400, 300))

    # Panel untuk menampung konten
    panel = wx.Panel(dialog)

    # Layout dialog
    sizer = wx.BoxSizer(wx.VERTICAL)

    # Penjelasan tentang mode Standard dan Left to Right dalam TextCtrl agar fokus bisa digunakan untuk pembaca layar
    explanation_text = _(
        "Standard Mode:\nCalculations follow the standard mathematical operator precedence rules (PEMDAS).\n"
        "Example: 3 + 5 * 2 = 13 (multiplication is performed first).\n\n"
        "Left to Right Mode:\nCalculations are performed from left to right without considering operator precedence.\n"
        "Example: 3 + 5 * 2 = 16 (calculations are done left to right).\n\n"        
        "Scientific Mode:\n\n"        
        "Sin and Cos:\nCalculates the values of sine and cosine.\n"
        "The input must be in degrees. The calculator will automatically convert the value to radians for the calculation.\n\n"        
        "Logarithms:\nTwo types of logarithms are available:\n"
        "- Natural Logarithm (LN): Logarithm with the natural base (e).\n"
        "- Base 10 Logarithm: Logarithm with base 10.\n"
        "Negative numbers are not supported as logarithms are only defined for positive numbers.\n\n"        
        "Square Root:\nCalculates the square root of a number.\n"
        "Negative numbers are not supported as the square root is only defined for non-negative numbers.\n\n"        
        "Result Format:\n"
        "- High Precision: Displays the result with full detail.\n"
        "- Rounded (2 Decimal Places): Displays the result in a simpler form, rounded to 2 decimal places for easier reading."
    )


    # Gunakan TextCtrl agar pembaca layar dapat membacanya dan fokus dapat dialihkan ke sini
    explanation = wx.TextCtrl(panel, value=explanation_text, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(380, 180))
    explanation.SetFocus()  # Set fokus pada TextCtrl agar pembaca layar langsung bisa membaca penjelasan
    sizer.Add(explanation, 1, wx.EXPAND | wx.ALL, 5)

    # Tombol OK
    ok_button = wx.Button(panel, label=_("OK"))
    ok_button.Bind(wx.EVT_BUTTON, lambda event: dialog.EndModal(wx.ID_OK))
    sizer.Add(ok_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

    # Tombol Escape untuk menutup dialog
    dialog.Bind(wx.EVT_CHAR_HOOK, lambda event: dialog.EndModal(wx.ID_CANCEL) if event.GetKeyCode() == wx.WXK_ESCAPE else event.Skip())

    # Set panel dan layout
    panel.SetSizerAndFit(sizer)

    # Menampilkan dialog
    dialog.ShowModal()

    # Setelah dialog ditutup, lakukan apa yang perlu dilakukan (misalnya log)
    dialog.Destroy()

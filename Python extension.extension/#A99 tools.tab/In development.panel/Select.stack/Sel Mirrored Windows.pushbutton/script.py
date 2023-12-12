# -*- coding: utf-8 -*-
__title__ = "Select mirrored windows"                         # Name of the button displayed in Revit UI
__doc__ = """Version = 1.0
Date    = 20.04.2022
_____________________________________________________________________
Description:
This script selects all mirrored windows with label value "#Okno"
_____________________________________________________________________
How-to:
-> Click on the button
-> Change Settings(optional)
-> Make a change
_____________________________________________________________________

To-Do:
- 
_____________________________________________________________________
Author: Jakub Dvořáček"""                                           # Button Description shown in Revit UI

# EXTRA: You can remove them.
__author__ = "Jakub Dvořáček"                                   # Script's Author
__helpurl__ = "https://atelier99cz.sharepoint.com/sites/Atelier99/SitePages/Main%20pages/BIM_Revit.aspx"     # Link that can be opened with F1 when hovered over the tool in Revit UI.

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
# Regular + Autodesk
from Autodesk.Revit.DB import Transaction                               # or Import only classes that are used.
from rpw import db, ui

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc   = __revit__.ActiveUIDocument.Document   # Document   class from RevitAPI that represents project. Used to Create, Delete, Modify and Query elements from the project.
uidoc = __revit__.ActiveUIDocument          # UIDocument class from RevitAPI that represents Revit project opened in the Revit UI.
app   = __revit__.Application                 # Represents the Autodesk Revit Application, providing access to documents, options and other application wide data and settings.


# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
# ==================================================

# Function to check if the window has the parameter 'Štítek' with value '#Okno'
def has_required_label(window):
    # Get the parameter definition by name
    param_def = None
    for p in window.Symbol.Parameters:
        if p.Definition.Name == "Štítek":
            param_def = p.Definition
            break

    if not param_def:
        return False

    param = window.Symbol.get_Parameter(param_def)
    if param:
        return param.AsString() == "#Okno"

    return False
# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
if __name__ == '__main__':

    t = Transaction(doc,__title__)  # Transactions are context-like objects that guard any changes made to a Revit model.

    t.Start()  # <- Transaction Start

    # Use the updated method for retrieving elements
    windows = db.Collector(of_category='Windows').get_elements(wrapped=True)
    mirrored_windows = [x for x in windows if getattr(x, 'Mirrored', False) and has_required_label(x)]
    msg = "There are " + str(len(mirrored_windows)) + " mirrored windows in the model"
    ui.forms.Alert(msg, title="Mirrored Windows")

    selection = ui.Selection(mirrored_windows)

    t.Commit()  # <- Transaction End
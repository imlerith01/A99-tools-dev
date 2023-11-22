# -*- coding: utf-8 -*-
__title__ = "Isolate selected warnings"                           # Name of the button displayed in Revit UI
__doc__ = """Version = 1.0
Date    = 21.11.2023
_____________________________________________________________________
Description:
This script isolates all elements with selected warnings in active view
_____________________________________________________________________
How-to:
-> Click on the button

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
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
clr.AddReference('System.Collections')

from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ElementId, Transaction
from Autodesk.Revit.UI import TaskDialog
from pyrevit import forms
from System.Collections.Generic import List

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
# GLOBAL VARIABLES

# - Place global variables here.

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
# ==================================================
# Main function to list warnings and isolate elements
def prepare_warnings_for_isolation(doc, uidoc):
    # Retrieve all warnings
    warnings = doc.GetWarnings()
    unique_warnings = set()

    # Process warnings to get unique descriptions
    for warning in warnings:
        unique_warnings.add(warning.GetDescriptionText())

    # Display checklist form using pyRevit forms
    selected_warnings = forms.SelectFromList.show(sorted(unique_warnings),
                                                  multiselect=True,
                                                  button_name='Isolate Elements')

    if selected_warnings:
        # Collect elements to isolate
        element_ids_to_isolate = set()
        for warning in warnings:
            if warning.GetDescriptionText() in selected_warnings:
                element_ids_to_isolate.update(warning.GetFailingElements())

        # Convert to ICollection[ElementId]
        element_ids = List[ElementId](element_ids_to_isolate)
        return element_ids
    return None

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝ CLASSES
# ==================================================

# - Place local classes here. If you might use any classes in other scripts, consider placing it in the lib folder.

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================

# Start a transaction to modify the document
with Transaction(doc, "Isolate Warnings") as trans:
    trans.Start()
    element_ids = prepare_warnings_for_isolation(doc, uidoc)
    if element_ids and element_ids.Count > 0:
        uidoc.ActiveView.IsolateElementsTemporary(element_ids)
    trans.Commit()

if element_ids:
    TaskDialog.Show("Isolation Complete", "Elements with the selected warnings have been isolated in the active view.")
else:
    TaskDialog.Show("Isolation Cancelled", "No warnings were selected for isolation.")

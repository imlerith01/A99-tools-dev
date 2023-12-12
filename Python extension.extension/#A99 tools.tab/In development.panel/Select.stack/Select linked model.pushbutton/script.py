# -*- coding: utf-8 -*-
__title__ = "Select linked\nmodels"                         # Name of the button displayed in Revit UI
__doc__ = """Version = 1.0
Date    = 20.04.2022
_____________________________________________________________________
Description:
This script selects linked models or dwg files
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
from pyrevit import revit, DB, forms
from System.Collections.Generic import List
from Autodesk.Revit.UI import TaskDialog

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc   = __revit__.ActiveUIDocument.Document   # Document   class from RevitAPI that represents project. Used to Create, Delete, Modify and Query elements from the project.
uidoc = __revit__.ActiveUIDocument          # UIDocument class from RevitAPI that represents Revit project opened in the Revit UI.
app   = __revit__.Application                 # Represents the Autodesk Revit Application, providing access to documents, options and other application wide data and settings.

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
def get_linked_models_and_dwg():
    linked_elements = []
    doc = revit.doc

    for elem in DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkInstance):
        file_name = elem.Name
        linked_elements.append((file_name, elem.Id))

    for elem in DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance):
        if elem.IsLinked:
            dwg_name = elem.Category.Name
            linked_elements.append((dwg_name, elem.Id))

    return linked_elements


def main():
    linked_elements = get_linked_models_and_dwg()

    if not linked_elements:
        forms.alert("There are no linked models or DWG files.", title="No Linked Elements")
        return

    selected_elements = forms.SelectFromList.show([x[0] for x in linked_elements], multiselect=True,
                                                  title="Select Linked Elements")

    if not selected_elements:
        forms.alert("No elements selected. Exiting.")
        return

    with revit.Transaction("Select Linked Elements"):
        selected_ids = List[DB.ElementId]()

        for elem_name, elem_id in linked_elements:
            if elem_name in selected_elements:
                selected_ids.Add(elem_id)

        revit.uidoc.Selection.SetElementIds(selected_ids)

if __name__ == "__main__":
    main()

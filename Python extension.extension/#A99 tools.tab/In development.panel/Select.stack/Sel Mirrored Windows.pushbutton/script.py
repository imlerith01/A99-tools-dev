# -*- coding: utf-8 -*-
__title__ = "Select mirrored windows"  # Name of the button displayed in Revit UI
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
Author: Jakub Dvořáček"""  # Button Description shown in Revit UI

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import TaskDialog
from System.Collections.Generic import List

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

def has_required_label(window):
    param = window.Symbol.LookupParameter("Štítek")
    if param and param.AsString() == "#Okno":
        return True
    return False

if __name__ == '__main__':
    t = Transaction(doc, __title__)
    t.Start()

    windows = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()
    mirrored_windows_ids = List[ElementId]()

    for window in windows:
        if window.Mirrored and has_required_label(window):
            mirrored_windows_ids.Add(window.Id)

    message = "There are {0} mirrored windows in the model.".format(mirrored_windows_ids.Count)
    TaskDialog.Show("Mirrored Windows", message)
    uidoc.Selection.SetElementIds(mirrored_windows_ids)

    t.Commit()

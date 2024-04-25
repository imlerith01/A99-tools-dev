# -*- coding: utf-8 -*-
__title__ = "Select \ncorrupted groups"                           # Name of the button displayed in Revit UI
__doc__ = """Version = 1.0
Date    = 21.11.2023
_____________________________________________________________________
Description:
This script selects groups with excluded elements
_____________________________________________________________________
How-to:
-> Click on the button

_____________________________________________________________________

To-Do:
- 
_____________________________________________________________________
Author: Jakub Dvořáček"""                                           # Button Description shown in Revit UI


import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import TaskDialog
from System.Collections.Generic import List

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

def find_corrupted_groups(doc):
    corrupted_groups_ids = List[ElementId]()  # Use .NET List to store ElementIds
    groups = FilteredElementCollector(doc).OfClass(Group).WhereElementIsNotElementType().ToElements()
    search_keyword = "vyloučené prvky"
    for group in groups:
        if search_keyword in group.Name:
            corrupted_groups_ids.Add(group.Id)  # Add ElementId to the .NET List
    return corrupted_groups_ids

t = Transaction(doc, __title__)
t.Start()

corrupted_groups_ids = find_corrupted_groups(doc)
message = 'There are {0} corrupted groups in the model.'.format(corrupted_groups_ids.Count)  # Use Count property of List
TaskDialog.Show('Corrupted groups', message)
uidoc.Selection.SetElementIds(corrupted_groups_ids)  # Pass the .NET List directly

t.Commit()
# -*- coding: utf-8 -*-
__title__ = "Rooms to floors"  # Name of the button displayed in Revit UI
__doc__ = """Version = 1.0
Date    = 20.04.2022
_____________________________________________________________________
Description:
This script creates floor by room outline
_____________________________________________________________________
How-to:
-> Click on the button

_____________________________________________________________________

To-Do:
- 
_____________________________________________________________________
Author: Jakub Dvořáček"""  # Button Description shown in Revit UI

# EXTRA: You can remove them.
__author__ = "Jakub Dvořáček"  # Script's Author
__helpurl__ = "https://atelier99cz.sharepoint.com/sites/Atelier99/SitePages/Main%20pages/BIM_Revit.aspx"  # Link that can be opened with F1 when hovered over the tool in Revit UI.

# IMPORTS
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType
from pyrevit import forms, script
from System.Collections.Generic import List
import os, sys, math, datetime, time

# VARIABLES
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
PATH_SCRIPT = os.path.dirname(__file__)

# FUNCTIONS

def select_rooms():
    """Select rooms in the Revit document."""
    try:
        selected_refs = uidoc.Selection.PickObjects(ObjectType.Element, "Select rooms")
        if not selected_refs:
            return []
        return [doc.GetElement(ref.ElementId) for ref in selected_refs]
    except Exception as e:
        return []

def get_floor_types():
    """Retrieve all available floor types from the Revit document."""
    all_floor_types = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsElementType().ToElements()
    all_floor_types = [f for f in all_floor_types if isinstance(f, FloorType)]
    return {Element.Name.GetValue(fr): fr for fr in all_floor_types}

def create_floors(rooms, floor_type):
    """Create floors in the selected rooms with the specified floor type."""
    floors_created = 0
    with Transaction(doc, "Create Floors") as trans:
        trans.Start()
        for room in rooms:
            level_id = room.LevelId
            boundary = room.GetBoundarySegments(SpatialElementBoundaryOptions())[0]
            curve_loop = CurveLoop.Create([seg.GetCurve() for seg in boundary])
            curve_loops = List[CurveLoop]()
            curve_loops.Add(curve_loop)
            if Floor.Create(doc, curve_loops, floor_type.Id, level_id):
                floors_created += 1
        trans.Commit()
    return floors_created

# MAIN
if __name__ == '__main__':
    rooms = select_rooms()
    if not rooms:
        forms.alert("No rooms selected. Exiting script.")
        script.exit()

    floor_types = get_floor_types()
    if not floor_types:
        forms.alert("No floor types found.")
        script.exit()

    selected_floor_type_name = forms.SelectFromList.show(sorted(floor_types.keys()), "Select a Floor Type")
    if not selected_floor_type_name:
        forms.alert("No floor type selected. Exiting script.")
        script.exit()

    selected_floor_type = floor_types[selected_floor_type_name]
    floors_created = create_floors(rooms, selected_floor_type)

    forms.alert('Floors created successfully: {} floors.'.format(floors_created))

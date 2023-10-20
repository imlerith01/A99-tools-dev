# -*- coding: utf-8 -*-
__title__ = "Join visible elements in active view"                  # Name of the button displayed in Revit UI
__doc__ = """Version = 1.0
Date    = 05.10.2023
_____________________________________________________________________
Description:

This tool will automatically join all selected element categories in view
_____________________________________________________________________
How-to:

-> Click on the button
-> Change Settings(optional)
_____________________________________________________________________
Last update:

_____________________________________________________________________
To-Do:
_____________________________________________________________________
Author: Jakub Dvoracek"""                                                      # Button Description shown in Revit UI

import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import (FilteredElementCollector, BuiltInCategory, JoinGeometryUtils,
                               Outline, BoundingBoxIntersectsFilter, Transaction)
from Autodesk.Revit.UI import TaskDialog

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# Import pyRevit forms
from pyrevit import forms

categories_dict = {
    "Walls": BuiltInCategory.OST_Walls,
    "Floors": BuiltInCategory.OST_Floors,
    "Ceilings": BuiltInCategory.OST_Ceilings
}


def join_intersecting_elements(selected_categories):
    elements = []
    for category in selected_categories:
        elements.extend(FilteredElementCollector(doc, uidoc.ActiveView.Id).OfCategory(
            category).WhereElementIsNotElementType().ToElements())

    t = Transaction(doc, 'Join Intersecting Elements')
    t.Start()

    join_count = 0

    for elem in elements:
        outline = Outline(elem.BoundingBox[uidoc.ActiveView].Min, elem.BoundingBox[uidoc.ActiveView].Max)
        bbFilter = BoundingBoxIntersectsFilter(outline)

        intersecting_elements = FilteredElementCollector(doc, uidoc.ActiveView.Id).WherePasses(bbFilter).ToElements()

        for other_elem in intersecting_elements:
            if elem.Id != other_elem.Id and not JoinGeometryUtils.AreElementsJoined(doc, elem, other_elem):
                try:
                    JoinGeometryUtils.JoinGeometry(doc, elem, other_elem)
                    join_count += 1
                except:
                    pass

    t.Commit()
    return join_count


# Use pyRevit forms for category selection
selected_categories = forms.SelectFromList.show(sorted(categories_dict.keys()), multiselect=True,
                                                title="Select Categories to Join")

if selected_categories:
    selected_categories = [categories_dict[cat] for cat in selected_categories]
    joined_elements_count = join_intersecting_elements(selected_categories)
    TaskDialog.Show('Info', '{} elements were successfully joined.'.format(joined_elements_count))


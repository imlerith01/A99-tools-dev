# -*- coding: utf-8 -*-
__title__ = "Isolate Painted Elements"
__doc__ = """Version = 1.0
Date    = 24.11.2023
_____________________________________________________________________
Description:
This script isolates painted elements in the active view.
_____________________________________________________________________
How-to:
-> Click on the button
-> Painted elements will be isolated in the active view
_____________________________________________________________________

To-Do:
- 
_____________________________________________________________________
Author: Jakub Dvořáček"""

__author__ = "Jakub Dvořáček"
__helpurl__ = "https://atelier99cz.sharepoint.com/sites/Atelier99/SitePages/Main%20pages/BIM_Revit.aspx"

import os
import clr
clr.AddReference("System")
from System.Collections.Generic import List
from Autodesk.Revit.DB import FilteredElementCollector, Transaction, Options, Solid, ElementId, ViewDetailLevel
from Autodesk.Revit.UI import TaskDialog

doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application
active_view = uidoc.ActiveView
PATH_SCRIPT = os.path.dirname(__file__)

# Function to check if an element is painted
def is_painted(element):
    geomOptions = Options()
    geomOptions.DetailLevel = ViewDetailLevel.Fine
    geomElement = element.get_Geometry(geomOptions)

    if geomElement is not None:
        for geomObj in geomElement:
            if isinstance(geomObj, Solid):
                for face in geomObj.Faces:
                    if doc.IsPainted(element.Id, face):
                        return True
    return False

if __name__ == '__main__':
    t = Transaction(doc, __title__)
    t.Start()

    try:
        painted_elements = List[ElementId]()
        elements = FilteredElementCollector(doc, active_view.Id).WhereElementIsNotElementType().ToElements()
        for element in elements:
            if is_painted(element):
                painted_elements.Add(element.Id)

        if painted_elements.Count > 0:
            active_view.IsolateElementsTemporary(painted_elements)
        else:
            TaskDialog.Show("Result", "No painted elements found in the active view.")
    except Exception as e:
        TaskDialog.Show("Error", "Error occurred: " + str(e))
        t.RollBack()
    else:
        t.Commit()
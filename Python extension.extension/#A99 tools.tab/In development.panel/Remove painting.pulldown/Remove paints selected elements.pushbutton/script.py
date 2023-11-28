# -*- coding: utf-8 -*-
__title__ = "Remove Paints from selected elements"
__doc__ = """Version = 1.0
Date    = 24.11.2023
_____________________________________________________________________
Description:
This script removes paint from user-selected elements in the Revit model.
_____________________________________________________________________
How-to:
-> Click on the button
-> Select elements from which you want to remove paint
-> Wait for the script to process the selected elements
-> Review the console output for the number of paints removed
_____________________________________________________________________

To-Do:
- 
_____________________________________________________________________
Author: Jakub Dvořáček"""

__author__ = "Jakub Dvořáček"
__helpurl__ = "https://atelier99cz.sharepoint.com/sites/Atelier99/SitePages/Main%20pages/BIM_Revit.aspx"

import os
from Autodesk.Revit.DB import Transaction, Options, Solid, ElementId
from Autodesk.Revit.UI.Selection import ObjectType

doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application
PATH_SCRIPT = os.path.dirname(__file__)

# GLOBAL VARIABLES
paints_removed = 0

def remove_paint(element):
    global paints_removed
    try:
        geomOptions = Options()
        geomElement = element.get_Geometry(geomOptions)

        if geomElement is not None:
            for geomObj in geomElement:
                if isinstance(geomObj, Solid):
                    for face in geomObj.Faces:
                        if doc.IsPainted(element.Id, face):
                            doc.RemovePaint(element.Id, face)
                            paints_removed += 1
    except Exception as e:
        print("Error in removing paint: " + str(e))

if __name__ == '__main__':
    t = Transaction(doc, __title__)
    t.Start()

    try:
        # Prompt user to select elements
        selected_ids = uidoc.Selection.PickObjects(ObjectType.Element, "Select elements to remove paint from")
        for sel_id in selected_ids:
            element = doc.GetElement(sel_id.ElementId)
            remove_paint(element)
    except Exception as e:
        print("Error in processing elements: " + str(e))
        t.RollBack()
    else:
        t.Commit()

# -*- coding: utf-8 -*-
__title__ = "Remove Paints"                          # Name of the button displayed in Revit UI
__doc__ = """Version = 1.0
Date    = 24.11.2023
_____________________________________________________________________
Description:
This script removes all paint from elements in the Revit model.
_____________________________________________________________________
How-to:
-> Click on the button
-> Wait for the script to process all elements
-> Review the console output for the number of paints removed
_____________________________________________________________________

To-Do:
- 
_____________________________________________________________________
Author: Jakub Dvořáček"""                                           # Button Description shown in Revit UI

__author__ = "Jakub Dvořáček"
__helpurl__ = "https://atelier99cz.sharepoint.com/sites/Atelier99/SitePages/Main%20pages/BIM_Revit.aspx"

import os
import sys
from Autodesk.Revit.DB import FilteredElementCollector, Transaction, Options, Solid

doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application
PATH_SCRIPT = os.path.dirname(__file__)

# GLOBAL VARIABLES
paints_removed = 0  # Counter for the number of paints removed

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
        elements = FilteredElementCollector(doc).WhereElementIsNotElementType().ToElements()
        for element in elements:
            remove_paint(element)
    except Exception as e:
        print("Error in processing elements: " + str(e))
        t.RollBack()
    else:
        t.Commit()

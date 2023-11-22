# -*- coding: utf-8 -*-
__title__ = "Room bounding elements"  # Name of the button displayed in Revit UI
__doc__ = """Version = 1.0
Date    = 22.11.2023
_____________________________________________________________________
Description:
This script gets all bounding elements of selected rooms
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

__author__ = "Jakub Dvořáček"  # Script's Author
__helpurl__ = "https://atelier99cz.sharepoint.com/sites/Atelier99/SitePages/Main%20pages/BIM_Revit.aspx"  # Help URL

# IMPORTS
from pyrevit import revit, DB
from pyrevit import forms
from pyrevit import script

# VARIABLES
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
output = script.get_output()

SEBO = DB.SpatialElementBoundaryOptions()  # Spatial Element Boundary Options for room boundary segments
BIC = DB.BuiltInCategory  # Shortcut for BuiltInCategory

# FUNCTIONS
def get_listOfBounding(r):
    """Retrieve list of bounding elements for a given room."""
    txt = ""
    ids = []
    for sub in r.GetBoundarySegments(SEBO):
        for bs in sub:
            i = bs.ElementId
            if i not in ids:
                ids.append(i)
                elem = doc.GetElement(i)
                if elem:
                    # Formatting output with element ID, category, and name
                    txt += output.linkify(elem.Id) + '; {}; {}\n'.format(elem.Category.Name, elem.Name)
                else:
                    txt += "None\n"
    return txt

# MAIN
if __name__ == '__main__':
    getName = lambda r: r.Parameter[DB.BuiltInParameter.ROOM_NAME].AsString()

    space = "\n---------------\n\n"

    with forms.WarningBar(title='Select Rooms to analyse'):
        elems = revit.pick_elements_by_category(BIC.OST_Rooms)
    if not elems:
        script.exit()

    print("LIST OF ALL THE SELECTED ROOMS AND THEIR BOUNDING ELEMENTS." \
          "\nRoom Number - Room Name\nId; Category; Name\n")
    for r in elems:
        print(space + r.Number + " - " + getName(r) + \
              "\n\n" + get_listOfBounding(r))

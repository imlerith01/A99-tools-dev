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

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
# Regular + Autodesk
import os
from Autodesk.Revit.DB import *                                     # Import everything from DB (Very good for beginners and during development)
from Autodesk.Revit.DB import Transaction, FilteredElementCollector # or Import only used classes.


# Custom Imports

# .NET Imports
import clr
clr.AddReference("System")
from System.Collections.Generic import List                         # List<ElementType>() <- it's special type of list from .NET framework that RevitAPI requires sometimes.

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
#==================================================
doc     = __revit__.ActiveUIDocument.Document                       # Document   class from RevitAPI that represents project. Used to Create, Delete, Modify and Query elements from the project.
uidoc   = __revit__.ActiveUIDocument                                # UIDocument class from RevitAPI that represents Revit project opened in the Revit UI(user interface).
app     = __revit__.Application                                     # Represents the Autodesk Revit Application, providing access to documents, options and other application wide data and settings.
active_view= doc.ActiveView                                         #Gets active view
# Global Settings


# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝
#==================================================

# Place local functions here. If you might use any functions in other scripts, consider placing it in the lib folder.



# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝
#==================================================

# Place local classes here. If you might use any classes in other scripts, consider placing it in the lib folder.

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================
all_walls= FilteredElementCollector(doc,active_view.Id).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
all_floors= FilteredElementCollector(doc,active_view.Id).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
all_ceilings= FilteredElementCollector(doc,active_view.Id).OfCategory(BuiltInCategory.OST_Ceilings).WhereElementIsNotElementType().ToElements()
all_elements= []
all_elements.extend(all_floors)
all_elements.extend(all_walls)
all_elements.extend(all_ceilings)

t = Transaction(doc, __title__)
t.Start()
intersecting_elements=[]
element_count =int(0)


for element1 in all_elements:
    for element2 in all_elements:
        geo1 = element1.get_Geometry(Options())
        filter_intersect = ElementIntersectsElementFilter(element1)

        if element1 is not element2:
            if filter_intersect.PassesFilter(element2) and (not JoinGeometryUtils.AreElementsJoined(doc, element1, element2)):
                intersecting_elements.append(element2)
                element_count += 1
                try:
                    JoinGeometryUtils.JoinGeometry(doc, element1, element2)
                except Exception as e:
                    # Handle any exceptions that occur during the join operation
                    print("Error joining walls:", str(e))
print(str(element_count) + " elements were joined")
t.Commit()

# -*- coding: utf-8 -*-
__title__ = "Create tiles"                           # Name of the button displayed in Revit UI
__doc__ = """Version = 1.0
Date    = 20.04.2022
_____________________________________________________________________
Description:
This is a template file for pyRevit Scripts.
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
# __highlight__ = "new"                                         # Button will have an orange dot + Description in Revit UI
# __min_revit_ver__ = 2021                                        # Limit your Scripts to certain Revit versions if it's not compatible due to RevitAPI Changes.
# __max_revit_ver = 2023                                          # Limit your Scripts to certain Revit versions if it's not compatible due to RevitAPI Changes.
# __context__     = ['Walls', 'Floors', 'Roofs']                # Make your button available only when certain categories are selected. Or Revit/View Types.

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
# Regular + Autodesk
import os, sys, math, datetime, time                                    # Regular Imports
from Autodesk.Revit.DB import *
import Autodesk
from Autodesk.Revit.DB import Transaction, FilteredElementCollector     # or Import only classes that are used.
from pyrevit import revit, DB
from pyrevit import forms
from pyrevit import script
# pyRevit
#from pyrevit import revit, forms                                        # import pyRevit modules. (Lots of useful features)

# Custom Imports
#from Snippets._selection import get_selected_elements                   # lib import
#from Snippets._convert import convert_internal_to_m                     # lib import

# .NET Imports
import clr                                  # Common Language Runtime. Makes .NET libraries accessinble
clr.AddReference("System")                  # Refference System.dll for import.
from System.Collections.Generic import List # List<ElementType>() <- it's special type of list from .NET framework that RevitAPI requires
# List_example = List[ElementId]()          # use .Add() instead of append or put python list of ElementIds in parentesis.

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc   = __revit__.ActiveUIDocument.Document   # Document   class from RevitAPI that represents project. Used to Create, Delete, Modify and Query elements from the project.
uidoc = __revit__.ActiveUIDocument          # UIDocument class from RevitAPI that represents Revit project opened in the Revit UI.
app   = __revit__.Application                 # Represents the Autodesk Revit Application, providing access to documents, options and other application wide data and settings.
PATH_SCRIPT = os.path.dirname(__file__)     # Absolute path to the folder where script is placed.

settings= Autodesk.Revit.DB.AreaVolumeSettings.GetAreaVolumeSettings(doc)
options = DB.SpatialElementBoundaryOptions()
b_option = settings.GetSpatialElementBoundaryLocation(SpatialElementType.Room)
options.SpatialElementBoundaryLocation = b_option
# GLOBAL VARIABLES

# - Place global variables here.

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
# ==================================================

def get_walls_types():
    """Retrieve all available floor types from the Revit document."""
    all_wall_types = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
    all_wall_types = [f for f in all_wall_types if isinstance(f, WallType)]
    return {Element.Name.GetValue(fr): fr for fr in all_wall_types}

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝ CLASSES
# ==================================================

# - Place local classes here. If you might use any classes in other scripts, consider placing it in the lib folder.

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
#Select rooms
getName = lambda r: r.Parameter[DB.BuiltInParameter.ROOM_NAME].AsString()

space = "\n---------------\n\n"
curvelist= []
levelidlist= []

with forms.WarningBar(title='Select Rooms to analyse'):
    elems = revit.pick_elements_by_category(BuiltInCategory.OST_Rooms)
if not elems:
    script.exit()
#Get room outline
for elem in elems:
    curves = []
    levelidlist.append(elem.LevelId)
    for boundlist in elem.GetBoundarySegments(options):
        for bound in boundlist:
            curves.append(bound.GetCurve())
    curvelist.append(curves)

t = Transaction(doc,__title__)
t.Start()  # <- Transaction Start

wall_types = get_walls_types()
if not wall_types:
    forms.alert("No wall types found.")
    script.exit()

selected_wall_type_name = forms.SelectFromList.show(sorted(wall_types.keys()), "Select a Wall Type")
if not selected_wall_type_name:
    forms.alert("No wall type selected. Exiting script.")
    script.exit()

# for curves in curvelist:
for curve in curves:
    wall= Wall.Create(doc, curve, elem.LevelId, False)

t.Commit()  # <- Transaction End
# -*- coding: utf-8 -*-
__title__ = "Select Elements By Category"                           # Name of the button displayed in Revit UI
__doc__ = """Version = 1.0
Date    = 20.04.2022
_____________________________________________________________________
Description:
Selects all elements in the user-chosen categories.
_____________________________________________________________________
How-to:
-> Click on the button
-> Choose categories from the list
-> Script will select all elements from those categories
_____________________________________________________________________

To-Do:
- 
_____________________________________________________________________
Author: Jakub Dvořáček"""                                           # Button Description shown in Revit UI

# EXTRA: You can remove them.
__author__ = "Jakub Dvořáček"                                   # Script's Author
__helpurl__ = "https://atelier99cz.sharepoint.com/sites/Atelier99/SitePages/Main%20pages/BIM_Revit.aspx"     # Link that can be opened with F1 when hovered over the tool in Revit UI.

# Regular + Autodesk
import os, sys, math, datetime, time                                    # Regular Imports
from Autodesk.Revit.DB import *                                         # Import everything from DB (Very good for beginners)

# pyRevit
from pyrevit import script, forms                                        # import pyRevit modules. (Lots of useful features)

# .NET Imports
import clr                                  # Common Language Runtime. Makes .NET libraries accessinble
clr.AddReference("System")                  # Refference System.dll for import.
from System.Collections.Generic import List # List<ElementType>() <- it's special type of list from .NET framework that RevitAPI requires

# VARIABLES
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# MAIN
if __name__ == '__main__':
    # Function to select elements in Revit
    def select_elements(element_ids):
        # Convert Python list to .NET List[ElementId]
        element_id_list = List[ElementId](element_ids)
        uidoc.Selection.SetElementIds(element_id_list)

    # Getting all categories
    categories = [cat for cat in doc.Settings.Categories if cat.AllowsBoundParameters]

    # Displaying categories to the user and allowing them to select
    selected_cat_names = forms.SelectFromList.show(
        sorted([cat.Name for cat in categories]),
        multiselect=True,
        title='Select Categories',
        button_name='Select'
    )

    if not selected_cat_names:
        script.exit()

    # Finding the corresponding Category objects for the names selected
    selected_categories = [cat for cat in categories if cat.Name in selected_cat_names]

    # Collecting elements from selected categories
    selected_element_ids = []
    for cat in selected_categories:
        cat_filter = ElementCategoryFilter(cat.Id)
        collector = FilteredElementCollector(doc).WherePasses(cat_filter).WhereElementIsNotElementType().ToElementIds()
        selected_element_ids.extend(collector)

    # Selecting elements in Revit
    select_elements(selected_element_ids)
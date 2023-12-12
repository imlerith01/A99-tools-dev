# -*- coding: utf-8 -*-
__title__ = "Cycle Family Types"
__doc__ = """Version = 1.0
Date    = 20.04.2022
...
Author: Jakub Dvořáček"""

# IMPORTS
import os
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import TaskDialog

# VARIABLES
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
# context: doc-family  # Uncomment this if it's required in your specific environment

# MAIN
if __name__ == '__main__':
    if not doc.IsFamilyDocument:
        TaskDialog.Show('Cycle Family Types', 'Must be in a Family Document.')
    else:
        family_types = [x for x in doc.FamilyManager.Types]
        sorted_type_names = sorted([x.Name for x in family_types])
        current_type = doc.FamilyManager.CurrentType

        next_family_type_name = None
        for n, type_name in enumerate(sorted_type_names):
            if type_name == current_type.Name:
                next_index = n + 1 if n + 1 < len(sorted_type_names) else 0
                next_family_type_name = sorted_type_names[next_index]
                break

        if next_family_type_name:
            for family_type in family_types:
                if family_type.Name == next_family_type_name:
                    t = Transaction(doc, __title__)
                    t.Start()
                    doc.FamilyManager.CurrentType = family_type
                    t.Commit()

                    message = 'Current type set to: {}'.format(next_family_type_name)
                    TaskDialog.Show('Cycle Family Types', message)
                    break

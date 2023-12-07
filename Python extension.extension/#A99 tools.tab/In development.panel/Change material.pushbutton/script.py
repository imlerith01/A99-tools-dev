# -*- coding: utf-8 -*-
__title__ = "Change material in \nall family types"
__doc__ = """Version = 1.0
Date    = 07.12.2023
_____________________________________________________________________
Description:
This script allows the user to select a Revit element, choose material parameters,
and apply a selected material to all family types of that element.
_____________________________________________________________________
How-to:
-> Click on the button
-> Select an element in Revit
-> Choose material parameters and material
-> The script will apply the selected material to all family types
_____________________________________________________________________

To-Do:
- 
_____________________________________________________________________
Author: Jakub Dvořáček"""

__author__ = "Jakub Dvořáček"
__helpurl__ = "https://atelier99cz.sharepoint.com/sites/Atelier99/SitePages/Main%20pages/BIM_Revit.aspx"

import os, sys, math, datetime, time
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType  # Import ObjectType
from pyrevit import revit, forms

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
PATH_SCRIPT = os.path.dirname(__file__)


# FUNCTIONS
# ==================================================

def get_material_params(element):
    return [param for param in element.Symbol.Parameters if
            param.Definition.ParameterGroup == BuiltInParameterGroup.PG_MATERIALS]


def prompt_parameter_selection(material_params):
    param_dict = {param.Definition.Name: param.Id for param in material_params}
    return forms.SelectFromList.show(sorted(param_dict.keys()), "Select parameters", 600, 600, multiselect=True)


def prompt_material_selection(document):
    materials = get_materials(document)
    selected_material_name = forms.SelectFromList.show(sorted(materials.keys()), "Select Material", 600, 300)
    return materials.get(selected_material_name)


def get_materials(document):
    collector = FilteredElementCollector(document).OfClass(Material)
    return {mat.Name: mat.Id for mat in collector}


def set_material_to_family_types(document, type_ids, param_names, material_id):
    for type_id in type_ids:
        family_symbol = document.GetElement(type_id)
        for param_name in param_names:
            parameter = family_symbol.LookupParameter(param_name)
            if parameter and parameter.StorageType == StorageType.ElementId:
                parameter.Set(material_id)


# MAIN
# ==================================================
if __name__ == '__main__':
    t = Transaction(doc, __title__)
    t.Start()

    try:
        selected_ref = uidoc.Selection.PickObject(ObjectType.Element, "Select an element.")
        if not selected_ref:
            raise Exception("No element selected")

        selected_element = doc.GetElement(selected_ref.ElementId)
        material_params = get_material_params(selected_element)

        if not material_params:
            raise Exception("Element doesn't have material parameters")

        selected_param_names = prompt_parameter_selection(material_params)
        if not selected_param_names:
            raise Exception("No parameters selected")

        selected_material_id = prompt_material_selection(doc)
        if not selected_material_id:
            raise Exception("No material selected")

        types_ids = selected_element.Symbol.Family.GetFamilySymbolIds()
        set_material_to_family_types(doc, types_ids, selected_param_names, selected_material_id)

    except Exception as e:
        forms.alert(str(e))
    finally:
        t.Commit()

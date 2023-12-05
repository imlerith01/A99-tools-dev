# -*- coding: utf-8 -*-
from pyrevit import revit, DB, script, forms
import clr
from Autodesk.Revit.DB import (FilteredElementCollector, Transaction, Material, StorageType, FamilySymbol,
                               BuiltInParameterGroup, FamilyInstance)
from Autodesk.Revit.UI.Selection import ObjectType


doc = revit.doc
uidoc = revit.uidoc

# Step 1: User selects 1 element
selected_ref = uidoc.Selection.PickObject(ObjectType.Element, "Select an element.")
selected_element = doc.GetElement(selected_ref.ElementId)

# Step 2: Display list of material parameters
material_params = []
for param in selected_element.Parameters:
    if param.Definition.ParameterGroup ==BuiltInParameterGroup.PG_MATERIALS:
        material_params.append(param)
material_params_type = []
for param_type in selected_element.Symbol.Parameters:
    if param_type.Definition.ParameterGroup ==BuiltInParameterGroup.PG_MATERIALS:
        material_params.append(param_type)

param_dict = {param.Definition.Name: param.Id for param in material_params}
selected_param_names = forms.SelectFromList.show(sorted(param_dict.keys()),
                                                 "Select parameters", 600, 600, multiselect=True)

def get_materials():
    collector = FilteredElementCollector(doc).OfClass(Material)
    return {mat.Name: mat.Id for mat in collector}

# Step 3: Choose material
materials = get_materials()
selected_material_name = forms.SelectFromList.show(sorted(materials.keys()), "Select Material", 600, 300)

#Get all family types
selected_family= selected_element.Symbol.Family
types_ids=selected_family.GetFamilySymbolIds()


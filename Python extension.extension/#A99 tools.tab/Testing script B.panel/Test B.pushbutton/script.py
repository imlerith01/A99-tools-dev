# -*- coding: utf-8 -*-
from pyrevit import revit, forms
from Autodesk.Revit.DB import FilteredElementCollector, Transaction, Material, BuiltInParameterGroup, StorageType
from Autodesk.Revit.UI.Selection import ObjectType

def main():
    # Get the current Revit document and UI document
    doc = revit.doc
    uidoc = revit.uidoc

    # Step 1: User selects an element
    selected_ref = uidoc.Selection.PickObject(ObjectType.Element, "Select an element.")
    if not selected_ref:
        return  # Exit if no element is selected

    selected_element = doc.GetElement(selected_ref.ElementId)

    # Step 2: Get and display material parameters of the selected element
    material_params = get_material_params(selected_element)
    if not material_params:
        forms.alert("Element doesn't have material parameters")
        return

    # Prompt the user to select parameters from the list
    selected_param_names = prompt_parameter_selection(material_params)
    if not selected_param_names:
        forms.alert("No parameters selected")
        return

    # Step 3: Prompt the user to choose a material
    selected_material_id = prompt_material_selection(doc)
    if not selected_material_id:
        forms.alert("No material selected")
        return

    # Get all family types of the selected element
    types_ids = selected_element.Symbol.Family.GetFamilySymbolIds()

    # Set the selected material to the chosen parameters for each family type
    set_material_to_family_types(doc, types_ids, selected_param_names, selected_material_id)

def get_material_params(element):
    """Get material parameters of the given element."""
    return [param for param in element.Symbol.Parameters if param.Definition.ParameterGroup == BuiltInParameterGroup.PG_MATERIALS]

def prompt_parameter_selection(material_params):
    """Prompt the user to select parameters from the material parameters."""
    param_dict = {param.Definition.Name: param.Id for param in material_params}
    return forms.SelectFromList.show(sorted(param_dict.keys()), "Select parameters", 600, 600, multiselect=True)

def prompt_material_selection(document):
    """Prompt the user to select a material from the document."""
    materials = get_materials(document)
    selected_material_name = forms.SelectFromList.show(sorted(materials.keys()), "Select Material", 600, 300)
    return materials.get(selected_material_name)

def get_materials(document):
    """Retrieve all materials from the given document."""
    collector = FilteredElementCollector(document).OfClass(Material)
    return {mat.Name: mat.Id for mat in collector}

def set_material_to_family_types(document, type_ids, param_names, material_id):
    """Set the selected material to the chosen parameters for each family type."""
    with Transaction(document, "Set Material Parameters") as trans:
        trans.Start()
        for type_id in type_ids:
            family_symbol = document.GetElement(type_id)
            for param_name in param_names:
                parameter = family_symbol.LookupParameter(param_name)
                if parameter and parameter.StorageType == StorageType.ElementId:
                    parameter.Set(material_id)
        trans.Commit()

if __name__ == "__main__":
    main()

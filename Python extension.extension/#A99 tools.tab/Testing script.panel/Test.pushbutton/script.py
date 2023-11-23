import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import FilteredElementCollector, Transaction, Material, StorageType, FamilySymbol, BuiltInParameterGroup, FamilyInstance
from Autodesk.Revit.UI.Selection import ObjectType
from pyrevit import forms

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

def get_materials():
    collector = FilteredElementCollector(doc).OfClass(Material)
    return {mat.Name: mat.Id for mat in collector}

def apply_material_to_family_symbols(family_symbols, material_id):
    with Transaction(doc, "Apply Material") as trans:
        trans.Start()
        for family_symbol in family_symbols:
            for param_id in selected_params:
                param = family_symbol.get_Parameter(param_id)
                if param and param.IsReadOnly == False:
                    param.Set(material_id)
        trans.Commit()

def get_material_type_parameters(element):
    if isinstance(element, FamilyInstance):
        element_type = doc.GetElement(element.Symbol.Id)
    else:
        element_type = doc.GetElement(element.GetTypeId())
    return [param for param in element_type.Parameters
            if param.StorageType == StorageType.ElementId
            and param.Definition.ParameterGroup == BuiltInParameterGroup.PG_MATERIALS]

# Step 1: Select element
selected_ref = uidoc.Selection.PickObject(ObjectType.Element, "Select an element")
element = doc.GetElement(selected_ref.ElementId)

# Step 2: Choose material type parameters
parameters = get_material_type_parameters(element)
param_dict = {param.Definition.Name: param.Id for param in parameters}
selected_param_names = forms.SelectFromList.show(sorted(param_dict.keys()), "Select Material Type Parameters", 600, 300, multiselect=True)
selected_params = [param_dict[name] for name in selected_param_names]

# Step 3: Choose material
materials = get_materials()
selected_material_name = forms.SelectFromList.show(sorted(materials.keys()), "Select Material", 600, 300)
selected_material_id = materials[selected_material_name]

# Step 4: Apply material
family_symbols = FilteredElementCollector(doc).OfClass(FamilySymbol).ToElements()
family_id = element.Symbol.Family.Id if isinstance(element, FamilyInstance) else element.Family.Id
family_symbols = [fs for fs in family_symbols if fs.Family.Id == family_id]
apply_material_to_family_symbols(family_symbols, selected_material_id)

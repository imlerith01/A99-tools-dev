from Autodesk.Revit.DB import FilteredElementCollector, FamilyInstance, Family, Transaction
from Autodesk.Revit.UI.Selection import ObjectType
from pyrevit import revit, DB, script, forms

# Function to get nested families
def get_nested_families(family):
    nested_families = []
    for family_symbol_id in family.GetFamilySymbolIds():
        nested_family_symbol = doc.GetElement(family_symbol_id)
        # Additional checks can be added here
        nested_families.append(nested_family_symbol.Family.Name)
    return nested_families

# Main script execution
doc = revit.doc
uidoc = revit.uidoc

# Prompt user to select a family instance
try:
    selected_ref = uidoc.Selection.PickObject(ObjectType.Element, "Select a family instance")
    selected_instance = doc.GetElement(selected_ref.ElementId)
    selected_family = selected_instance.Symbol.Family

    # Get nested families
    nested_families = get_nested_families(selected_family)

    # Display results
    if nested_families:
        forms.alert('Nested Families:\n' + '\n'.join(nested_families), exitscript=True)
    else:
        forms.alert('No nested families found.', exitscript=True)
except Exception as e:
    forms.alert('Error or operation cancelled by user: {}'.format(str(e)), exitscript=True)

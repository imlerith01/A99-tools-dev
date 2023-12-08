import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType
from pyrevit import forms, script

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# Function to select rooms
def select_rooms():
    selected_refs = uidoc.Selection.PickObjects(ObjectType.Element, "Select rooms")
    rooms = [doc.GetElement(ref.ElementId) for ref in selected_refs if doc.GetElement(ref.ElementId).Category.Name == 'Rooms']
    return rooms

# Function to get all floor type names
def get_floor_type_names():
    floor_types = FilteredElementCollector(doc).OfClass(FloorType).ToElements()
    floor_type_names = [ft.Name for ft in floor_types]
    return floor_type_names

# Function to get floor type by name
def get_floor_type_by_name(name):
    floor_types = FilteredElementCollector(doc).OfClass(FloorType).ToElements()
    for ft in floor_types:
        if ft.Name == name:
            return ft
    return None

# Function to create floor for each room
def create_floors(rooms, floor_type):
    with Transaction(doc, "Create Floors") as trans:
        trans.Start()
        for room in rooms:
            level_id = room.LevelId
            boundary = room.GetBoundarySegments(SpatialElementBoundaryOptions())[0]
            curve_loop = CurveLoop.Create([seg.GetCurve() for seg in boundary])
            floor = Floor.Create(doc, curve_loop, floor_type.Id, level_id)
        trans.Commit()

# Main script execution
# Step 1: Select rooms
rooms = select_rooms()
if not rooms:
    script.exit()

# Step 2: Choose floor type
floor_type_names = get_floor_type_names()

if not floor_type_names:
    forms.alert("No floor types found.")
    script.exit()

selected_floor_type_name = forms.SelectFromList.show(sorted(floor_type_names), "Select a Floor Type")

if not selected_floor_type_name:
    script.exit()

selected_floor_type = get_floor_type_by_name(selected_floor_type_name)

# Step 3: Create floors
create_floors(rooms, selected_floor_type)
forms.alert('Floors created successfully.')

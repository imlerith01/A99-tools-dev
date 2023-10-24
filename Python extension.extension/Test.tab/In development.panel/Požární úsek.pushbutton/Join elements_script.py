from pyrevit import forms
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction, DirectShape, DirectShapeType, ElementId, TessellatedShapeBuilder, TessellatedShapeBuilderTarget, TessellatedShapeBuilderFallback, TessellatedFace
from Autodesk.Revit.DB.Architecture import Room
from Autodesk.Revit.DB import XYZ
from pyrevit import revit, DB

# Get the current document and UI document
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# Collect all rooms in the document
rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).ToElements()

# Create a dictionary to map room names and numbers to room objects
room_dict = {}
for room in rooms:
    room_name = room.LookupParameter('Name').AsString() if room.LookupParameter('Name') else "Unnamed"
    room_number = room.LookupParameter('Number').AsString() if room.LookupParameter('Number') else "Unnumbered"
    room_dict["{} - {}".format(room_name, room_number)] = room

# Show the UI to the user to select rooms
selected_room_strings = forms.SelectFromList.show(list(room_dict.keys()), multiselect=True, button_name='Select Rooms')

# Map the selected strings back to room objects
selected_rooms = [room_dict[room_str] for room_str in selected_room_strings] if selected_room_strings else []

# Check if the user canceled the selection
if not selected_rooms:
    print("User canceled. Exiting.")
    exit()

# Start a new transaction
with Transaction(doc, "Create DirectShape Masses for Selected Rooms") as t:
    t.Start()

    # Loop through selected rooms and create DirectShape mass
    for room in selected_rooms:
        # Get room boundary and create mass
        boundary = room.GetBoundarySegments(DB.SpatialElementBoundaryOptions())
        if boundary:  # Check if boundary is not None
            # Convert boundary to suitable geometry for DirectShape (e.g., TessellatedShapeBuilder)
            builder = TessellatedShapeBuilder()
            builder.OpenConnectedFaceSet()
            # Assuming boundary is a list of XYZ points
            for segment in boundary[0]:
                start_point = segment.GetCurve().GetEndPoint(0)
                end_point = segment.GetCurve().GetEndPoint(1)
                # Create TessellatedFace (you'll need to define the points and normals)
                face = TessellatedFace([start_point, end_point, XYZ(0, 0, 0)], XYZ.BasisZ)
                builder.AddFace(face)
            builder.CloseConnectedFaceSet()
            builder.Target = TessellatedShapeBuilderTarget.Solid
            builder.Fallback = TessellatedShapeBuilderFallback.Mesh
            result = builder.Build()

            if result.Outcome == TessellatedShapeBuilderOutcome.Nothing:
                print("Failed to create DirectShape for room {}".format(room.LookupParameter('Name').AsString()))
                continue

            # Create DirectShape
            ds_type = DirectShapeType.Create(doc, "Room Mass", ElementId(BuiltInCategory.OST_GenericModel))
            ds = DirectShape.CreateElement(doc, ds_type.Id)
            ds.SetShape(result.GetGeometricalObjects())

    t.Commit()

print("DirectShape masses created for selected rooms.")

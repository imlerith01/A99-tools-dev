import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

from Autodesk.Revit.DB import FilteredElementCollector, Dimension, Transaction, ReferenceArray
from Autodesk.Revit.DB import Line, XYZ

doc = __revit__.ActiveUIDocument.Document
view = __revit__.ActiveUIDocument.ActiveGraphicalView

# Function to get all dimensions in the active view
def get_dimensions(view):
    return FilteredElementCollector(doc, view.Id).OfClass(Dimension)

# Function to recreate a dimension
def recreate_dimension(dimension):
    # Extract necessary properties from the old dimension
    line = dimension.Curve
    references = dimension.References

    refArray = ReferenceArray()
    for ref in references:
        refArray.Append(ref)

    # Create a new dimension
    new_dimension = None
    if refArray.Size > 1:
        new_dimension = doc.Create.NewDimension(view, line, refArray)

    return new_dimension

# Start a transaction to modify the document
t = Transaction(doc, 'Delete and Recreate Dimensions')
t.Start()

try:
    dimensions = get_dimensions(view)
    for dimension in dimensions:
        # Recreate the dimension
        new_dimension = recreate_dimension(dimension)

        # Delete the old dimension if new one is created
        if new_dimension:
            doc.Delete(dimension.Id)

    t.Commit()
except Exception as e:
    print("Error:", e)
    t.RollBack()

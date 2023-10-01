# Import necessary libraries
from Autodesk.Revit.DB import FilteredElementCollector, Transaction, BuiltInCategory, ElementId
from Autodesk.Revit.UI import TaskDialog
from System.Collections.Generic import List
import pyrevit.forms

# Get the current document
doc = __revit__.ActiveUIDocument.Document


# Define a function to join intersecting elements from selected categories
def join_intersecting_elements(selected_categories):
    # Create a transaction to make changes
    t = Transaction(doc, "Join Intersecting Elements")
    t.Start()

    try:
        # Loop through each selected category
        for category in selected_categories:
            # Get the corresponding BuiltInCategory from the user-friendly name
            built_in_category = category_to_built_in_category[category]

            # Create a filtered element collector for the selected category
            element_collector = FilteredElementCollector(doc).OfCategory(
                built_in_category).WhereElementIsNotElementType()

            # Loop through elements in the selected category
            for element in element_collector:
                if element.Location:
                    # Check if elements from the same category intersect
                    intersecting_elements = [other for other in element_collector if
                                             element.Id != other.Id and element.get_Geometry(None).Intersect(
                                                 other.get_Geometry(None))]
                    for other_element in intersecting_elements:
                        # Create a collection of ElementIds to join
                        elements_to_join = List[ElementId]()
                        elements_to_join.Add(element.Id)
                        elements_to_join.Add(other_element.Id)

                        # Join the elements using JoinGeometryUtils
                        JoinGeometryUtils.JoinGeometry(doc, elements_to_join)

        # Commit the transaction
        t.Commit()
    except Exception as ex:
        t.RollBack()
        TaskDialog.Show("Error", str(ex))


# Create a dictionary to map user-friendly names to BuiltInCategories
category_to_built_in_category = {
    "Walls": BuiltInCategory.OST_Walls,
    "Floors": BuiltInCategory.OST_Floors,
    "Ceilings": BuiltInCategory.OST_Ceilings,
}

# Create a list of user-friendly categories to choose from
categories_to_choose = list(category_to_built_in_category.keys())

# Create a category selection dialog with multiselect enabled
selected_categories = pyrevit.forms.SelectFromList.show(
    categories_to_choose,
    title="Select Categories to Join",
    button_name="Select Categories",
    multiselect=True
)

# Check if the user selected categories
if selected_categories:
    # Call the function to join intersecting elements from selected categories
    join_intersecting_elements(selected_categories)
else:
    TaskDialog.Show("Info", "No categories selected. The script was canceled.")

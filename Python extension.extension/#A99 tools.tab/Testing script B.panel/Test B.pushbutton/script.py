import clr
import Autodesk.Revit.DB as DB
import Autodesk.Revit.UI as UI
from pyrevit import forms

# Add references to Revit API
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')

# Import Document Manager
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Get the active document
doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = uiapp.ActiveUIDocument

# Function to list all linked models
def list_linked_models():
    collector = DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkInstance)
    return collector

# Function to get the survey point location
def get_survey_point_location():
    # Assuming you want the Project Base Point
    base_point = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_ProjectBasePoint).ToElements()[0]
    point = base_point.get_BoundingBox(None).Min
    return point

# Function to set the coordinates to the selected model
def set_coordinates_to_model(link_instance, new_location):
    TransactionManager.Instance.EnsureInTransaction(doc)
    try:
        link_instance.get_Parameter(DB.BuiltInParameter.BASEPOINT_EASTWEST_PARAM).Set(new_location.X)
        link_instance.get_Parameter(DB.BuiltInParameter.BASEPOINT_NORTHSOUTH_PARAM).Set(new_location.Y)
        link_instance.get_Parameter(DB.BuiltInParameter.BASEPOINT_ELEVATION_PARAM).Set(new_location.Z)
    except Exception as e:
        print("Error setting coordinates: {}".format(str(e)))
    finally:
        TransactionManager.Instance.TransactionTaskDone()

def main():
    # List all linked models
    linked_models = list_linked_models()

    # Create a dictionary to map model names to their instances
    model_dict = {lm.Name: lm for lm in linked_models}

    # Ask user to select a model from the list
    selected_model_name = forms.SelectFromList.show(
        sorted(model_dict.keys()),
        title='Select a Linked Model',
        multiselect=False
    )

    if not selected_model_name:
        forms.alert('No model selected, script will exit.')
        return

    # Get the selected model instance
    selected_model = model_dict[selected_model_name]

    # Get the survey point location
    survey_point_location = get_survey_point_location()

    # Set the coordinates to the selected model
    set_coordinates_to_model(selected_model, survey_point_location)

    # Inform the user
    forms.alert('Coordinates set to the selected linked model.')

main()
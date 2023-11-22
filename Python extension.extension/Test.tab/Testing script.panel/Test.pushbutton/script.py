import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
clr.AddReference('System.Collections')

from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ElementId, Transaction
from Autodesk.Revit.UI import TaskDialog
from pyrevit import forms
from System.Collections.Generic import List

# Main function to list warnings and isolate elements
def isolate_warnings_elements(doc, uidoc):
    # Retrieve all warnings
    warnings = doc.GetWarnings()
    unique_warnings = set()

    # Process warnings to get unique descriptions
    for warning in warnings:
        unique_warnings.add(warning.GetDescriptionText())

    # Display checklist form using pyRevit forms
    selected_warnings = forms.SelectFromList.show(sorted(unique_warnings),
                                                  multiselect=True,
                                                  button_name='Isolate Elements')

    if selected_warnings:
        # Collect elements to isolate
        element_ids_to_isolate = set()
        for warning in warnings:
            if warning.GetDescriptionText() in selected_warnings:
                element_ids_to_isolate.update(warning.GetFailingElements())

        # Convert to ICollection[ElementId]
        element_ids = List[ElementId](element_ids_to_isolate)

        # Start a transaction to modify the document
        with Transaction(doc, "Isolate Warnings") as trans:
            trans.Start()
            view = uidoc.ActiveView
            # Isolate elements
            if element_ids.Count > 0:
                view.IsolateElementsTemporary(element_ids)
            trans.Commit()

        TaskDialog.Show("Isolation Complete", "Elements with the selected warnings have been isolated in the active view.")

# Boilerplate code
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

isolate_warnings_elements(doc, uidoc)

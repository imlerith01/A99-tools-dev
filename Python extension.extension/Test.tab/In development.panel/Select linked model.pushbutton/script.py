# -*- coding: utf-8 -*-
from pyrevit import revit, DB, forms
from System.Collections.Generic import List
from Autodesk.Revit.UI import TaskDialog


def get_linked_models_and_dwg():
    linked_elements = []
    doc = revit.doc

    for elem in DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkInstance):
        file_name = elem.Name
        linked_elements.append((file_name, elem.Id))

    for elem in DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance):
        if elem.IsLinked:
            dwg_name = elem.Category.Name
            linked_elements.append((dwg_name, elem.Id))

    return linked_elements


def main():
    linked_elements = get_linked_models_and_dwg()

    if not linked_elements:
        forms.alert("There are no linked models or DWG files.", title="No Linked Elements")
        return

    selected_elements = forms.SelectFromList.show([x[0] for x in linked_elements], multiselect=True,
                                                  title="Select Linked Elements")

    if not selected_elements:
        forms.alert("No elements selected. Exiting.")
        return

    with revit.Transaction("Select Linked Elements"):
        selected_ids = List[DB.ElementId]()

        for elem_name, elem_id in linked_elements:
            if elem_name in selected_elements:
                selected_ids.Add(elem_id)

        revit.uidoc.Selection.SetElementIds(selected_ids)

if __name__ == "__main__":
    main()

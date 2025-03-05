# -*- coding: utf-8 -*-

"""
Selects all elements that share the same Reference Level as the selected element.

TESTED REVIT API: 2023

Author: Robert Perry Lackowski (modified for Revit 2023)
"""

from Autodesk.Revit.DB import ElementLevelFilter, FilteredElementCollector
from Autodesk.Revit.DB import Document, BuiltInParameter, BuiltInCategory, ElementFilter, ElementCategoryFilter, LogicalOrFilter, ElementIsElementTypeFilter, ElementId
from Autodesk.Revit.Exceptions import OperationCanceledException
# from pyrevit import DB
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

from rpw import ui

import sys

# Ask user to pick an object which has the desired reference level
def pick_object():
    from Autodesk.Revit.UI.Selection import ObjectType

    try:
        picked_object = uidoc.Selection.PickObject(ObjectType.Element, "Select an element.")
        if picked_object:
            selected_elem = doc.GetElement(picked_object.ElementId)
            print("Selected Element: {0}, ID: {1}".format(selected_elem.Name, picked_object.ElementId))
            return selected_elem
        else:
            print("No element selected.")
            sys.exit()
    except OperationCanceledException:
        print("Selection canceled.")
        sys.exit()

def get_level_id(elem):
    # If the element is of category "Levels" (Podlaží), return its ID
    if elem.Category and elem.Category.Name == "Podlaží":  # "Podlaží" means "Levels" in Czech
        print("The selected element is a Level. Using its ID directly.")
        return elem.Id

    # List of BuiltInParameters to try to extract a level ID
    BIPs = [
        BuiltInParameter.CURVE_LEVEL,
        BuiltInParameter.DPART_BASE_LEVEL_BY_ORIGINAL,
        BuiltInParameter.DPART_BASE_LEVEL,
        BuiltInParameter.FACEROOF_LEVEL_PARAM,
        BuiltInParameter.FAMILY_BASE_LEVEL_PARAM,
        BuiltInParameter.FAMILY_LEVEL_PARAM,
        BuiltInParameter.GROUP_LEVEL,
        BuiltInParameter.IMPORT_BASE_LEVEL,
        BuiltInParameter.INSTANCE_REFERENCE_LEVEL_PARAM,
        BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM,
        BuiltInParameter.LEVEL_PARAM,
        BuiltInParameter.MULTISTORY_STAIRS_REF_LEVEL,
        BuiltInParameter.PATH_OF_TRAVEL_LEVEL_NAME,
        BuiltInParameter.PLAN_VIEW_LEVEL,
        BuiltInParameter.ROOF_BASE_LEVEL_PARAM,
        BuiltInParameter.ROOF_CONSTRAINT_LEVEL_PARAM,
        BuiltInParameter.ROOM_LEVEL_ID,
        BuiltInParameter.SCHEDULE_BASE_LEVEL_PARAM,
        BuiltInParameter.SCHEDULE_LEVEL_PARAM,
        BuiltInParameter.SLOPE_ARROW_LEVEL_END,
        BuiltInParameter.STAIRS_BASE_LEVEL,
        BuiltInParameter.STAIRS_BASE_LEVEL_PARAM,
        BuiltInParameter.STAIRS_RAILING_BASE_LEVEL_PARAM,
        BuiltInParameter.STRUCTURAL_REFERENCE_LEVEL_ELEVATION,
        BuiltInParameter.SYSTEM_ZONE_LEVEL_ID,
        BuiltInParameter.TRUSS_ELEMENT_REFERENCE_LEVEL_PARAM,
        BuiltInParameter.VIEW_GRAPH_SCHED_BOTTOM_LEVEL,
        BuiltInParameter.VIEW_UNDERLAY_BOTTOM_ID,
        BuiltInParameter.WALL_BASE_CONSTRAINT,
        BuiltInParameter.WALL_SWEEP_LEVEL_PARAM
    ]

    level_id = None

    print("Attempting to get level ID for element: {0}".format(elem.Name))

    for BIP in BIPs:
        param = elem.get_Parameter(BIP)
        if param:
            param_elem_id = param.AsElementId()
            if param_elem_id.Compare(ElementId.InvalidElementId) == 1:
                level_id = param_elem_id
                print("Level found for {0} with BuiltInParameter {1}: {2}".format(elem.Name, BIP, level_id))
                return level_id

    try:
        level_id = elem.LevelId
        if level_id.Compare(ElementId.InvalidElementId) == 1:
            print("Level found using LevelId property: {0}".format(level_id))
            return level_id
    except AttributeError:
        pass

    try:
        level_id = elem.ReferenceLevel.Id
        if level_id.Compare(ElementId.InvalidElementId) == 1:
            print("Level found using ReferenceLevel.Id: {0}".format(level_id))
            return level_id
    except AttributeError:
        pass

    print("No level ID found for the selected element.")
    return None

# Get selected element, either from current selection or a new selection
selection = ui.Selection()

if selection:
    selected_element = selection[0]
    print("Selected element from current selection: {0}".format(selected_element.Name))
else:
    selected_element = pick_object()

target_level_id = get_level_id(selected_element)

if target_level_id is not None:
    print("Target Level ID: {0}".format(target_level_id))

    # Create a filter based on categories
    BICs = [
        BuiltInCategory.OST_CableTray,
        BuiltInCategory.OST_CableTrayFitting,
        BuiltInCategory.OST_Conduit,
        BuiltInCategory.OST_ConduitFitting,
        BuiltInCategory.OST_DuctCurves,
        BuiltInCategory.OST_DuctFitting,
        BuiltInCategory.OST_DuctTerminal,
        BuiltInCategory.OST_ElectricalEquipment,
        BuiltInCategory.OST_ElectricalFixtures,
        BuiltInCategory.OST_FloorOpening,
        BuiltInCategory.OST_Floors,
        BuiltInCategory.OST_FloorsDefault,
        BuiltInCategory.OST_LightingDevices,
        BuiltInCategory.OST_LightingFixtures,
        BuiltInCategory.OST_MechanicalEquipment,
        BuiltInCategory.OST_PipeCurves,
        BuiltInCategory.OST_PipeFitting,
        BuiltInCategory.OST_PlumbingFixtures,
        BuiltInCategory.OST_RoofOpening,
        BuiltInCategory.OST_Roofs,
        BuiltInCategory.OST_RoofsDefault,
        BuiltInCategory.OST_SpecialityEquipment,
        BuiltInCategory.OST_Sprinklers,
        BuiltInCategory.OST_StructuralStiffener,
        BuiltInCategory.OST_StructuralTruss,
        BuiltInCategory.OST_StructuralColumns,
        BuiltInCategory.OST_StructuralFraming,
        BuiltInCategory.OST_StructuralFramingSystem,
        BuiltInCategory.OST_StructuralFramingOther,
        BuiltInCategory.OST_StructuralFramingOpening,
        BuiltInCategory.OST_StructuralFoundation,
        BuiltInCategory.OST_Walls,
        BuiltInCategory.OST_Wire,
    ]

    category_filters = []

    for BIC in BICs:
        category_filters.append(ElementCategoryFilter(BIC))

    final_filter = LogicalOrFilter(category_filters)

    # Apply filter to create list of elements
    all_elements = FilteredElementCollector(doc).WherePasses(final_filter).WhereElementIsNotElementType().WhereElementIsViewIndependent().ToElements()

    print("Number of elements after filtering: {0}".format(len(all_elements)))

    selection.clear()

    for elem in all_elements:
        elem_level_id = get_level_id(elem)
        if elem_level_id == target_level_id:
            print("Element {0} shares the same level. Adding to selection.".format(elem.Name))
            selection.add(elem)

    selection.update()

else:
    print("No level associated with selected element.")

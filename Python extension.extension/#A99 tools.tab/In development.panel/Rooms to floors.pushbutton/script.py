# -*- coding: utf-8 -*-
__title__     = "Rooms to Floors"
__author__    = "Jakub Dvořáček"
__doc__       = """
Date    = 19.02.2024
_____________________________________________________________________
Description:

Create Floors from selected Rooms. 
New Floors will be selected once created.
_____________________________________________________________________
"""

import traceback

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#==================================================
from Autodesk.Revit.DB import *

# .NET IMPORTS
import clr
clr.AddReference("System")
from System.Collections.Generic import List

from pyrevit import revit, DB
from pyrevit import forms
from pyrevit import script


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
#==================================================
uidoc    = __revit__.ActiveUIDocument
app      = __revit__.Application
doc      = __revit__.ActiveUIDocument.Document
rvt_year = int(app.VersionNumber)

active_view_id      = doc.ActiveView.Id
active_view         = doc.GetElement(active_view_id)
active_view_level   = active_view.GenLevel

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝
class FloorsCreationWarningSwallower(IFailuresPreprocessor):
    def PreprocessFailures(self, failuresAccessor):
        failList = failuresAccessor.GetFailureMessages()
        for failure in failList: #type: FailureMessage
            failuresAccessor.DeleteWarning(failure)
            # print(failure)
            # fail_id = failure.GetFailureDefinitionId()
            # if fail_id == BuiltInFailures.OverlapFailures.FloorsOverlap:
            #     failuresAccessor.DeleteWarning(failure)
            # elif fail_id == BuiltInFailures.ExtrusionFailures.CannotDrawExtrusionsError:
            #     failuresAccessor.DeleteWarning(failure)

        return FailureProcessingResult.Continue

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
#==================================================
def select_floor_type():
    """Function to display GUI and let user select Floor Type.
    :return:  Selected FloorType """
    all_floor_types = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsElementType().ToElements()
    all_floor_types = [f for f in all_floor_types if type(f) == FloorType] # Filter ModelledInPlace Elements.
    dict_floor_types = {Element.Name.GetValue(fr): fr for fr in all_floor_types}
    selected_elements = select_from_dict(dict_floor_types,
                                         title = __title__, label='Select FloorType',
                                         button_name='Select', version=__version__,
                                         SelectMultiple=False)
    if selected_elements:
        return selected_elements[0]
    forms.alert("No FloorType was selected. \nPlease, select a FloorType and Try Again.", title=__title__, exitscript=True)


def room_to_floor(room, floor_type, offset):
    new_floor = None
    try:
        # Make sure that Room is bounding.
        if not room.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble():
            return None

        #  ROOM BOUNDARIES
        room_boundaries = room.GetBoundarySegments(SpatialElementBoundaryOptions())
        floor_shape = room_boundaries[0]
        openings = list(room_boundaries)[1:] if len(room_boundaries) > 1 else []


        if rvt_year >= 2022:
            with Transaction(doc, 'Create FloorOpening') as t:
                t.Start()
                List_curve_loop = List[CurveLoop]()
                for room_outline in room_boundaries:
                    curve_loop = CurveLoop()
                    for seg in room_outline:
                        curve_loop.Append(seg.GetCurve())
                    List_curve_loop.Add(curve_loop)
                new_floor = Floor.Create(doc, List_curve_loop, floor_type.Id, active_view_level.Id) #FIXME
                if new_floor:
                    # SET OFFSET
                    param = new_floor.get_Parameter(BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM)
                    param.Set(offset)

                failOpt = t.GetFailureHandlingOptions()
                failOpt.SetFailuresPreprocessor(FloorsCreationWarningSwallower())
                t.SetFailureHandlingOptions(failOpt)

                t.Commit()


    except:
        # print(traceback.format_exc())
        pass

    if new_floor:
        return new_floor



def create_floors(selected_rooms, selected_floor_type, offset):
    """Function to loop through selected rooms and create floors from them."""
    new_floors = []

    with TransactionGroup(doc, __title__) as tg:
        tg.Start()
        for r in selected_rooms:
            new_floor = room_to_floor(room = r, floor_type=selected_floor_type, offset = offset)
            if new_floor:
                new_floors.append(new_floor)
        tg.Assimilate()
    return new_floors


def get_floor_types():
    """Retrieve all available floor types from the Revit document."""
    all_floor_types = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsElementType().ToElements()
    all_floor_types = [f for f in all_floor_types if isinstance(f, FloorType)]
    return {Element.Name.GetValue(fr): fr for fr in all_floor_types}


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝MAIN
#==================================================
if __name__ == '__main__':
    with forms.WarningBar(title='Select Rooms'):
        selected_rooms = revit.pick_elements_by_category(BuiltInCategory.OST_Rooms)
    if not selected_rooms:
        script.exit()
    if not selected_rooms:
        script.exit()
    floor_types = get_floor_types()
    if not floor_types:
        forms.alert("No wall types found.")
        script.exit()
    selected_floor_type_name = forms.SelectFromList.show(sorted(floor_types.keys()), "Select a Floor Type")
    if not selected_floor_type_name:
        forms.alert("No floor type selected. Exiting script.")
        script.exit()
    selected_floor_type_id = floor_types[selected_floor_type_name].Id

    new_floors = create_floors(selected_rooms, selected_floor_type_id, 0)



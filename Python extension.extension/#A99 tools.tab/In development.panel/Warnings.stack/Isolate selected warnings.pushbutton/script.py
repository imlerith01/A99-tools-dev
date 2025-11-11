# -*- coding: utf-8 -*-
__title__ = "Isolate selected warnings"                           # Name of the button displayed in Revit UI
__doc__ = """Version = 1.1
Date    = 18.09.2025
_____________________________________________________________________
Description:
This script isolates all elements with selected warnings in active view.
If a failing element is a curtain wall mullion/panel, the host curtain wall is isolated instead.
_____________________________________________________________________
How-to:
-> Click on the button
_____________________________________________________________________
To-Do:
-
_____________________________________________________________________
Author: Jakub Dvořáček"""                                           # Button Description shown in Revit UI

# EXTRA: You can remove them.
__author__ = "Jakub Dvořáček"
__helpurl__ = "https://atelier99cz.sharepoint.com/sites/Atelier99/SitePages/Main%20pages/BIM_Revit.aspx"

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
clr.AddReference('System.Collections')

from Autodesk.Revit.DB import (
    FilteredElementCollector, BuiltInCategory, BuiltInParameter,
    ElementId, Transaction, Wall
)
from Autodesk.Revit.UI import TaskDialog
from pyrevit import forms
from System.Collections.Generic import List

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
# ==================================================
def _is_curtain_subcategory(cat_id_int):
    return cat_id_int in (
        int(BuiltInCategory.OST_CurtainWallMullions),
        int(BuiltInCategory.OST_CurtainWallPanels),
    )

def _get_host_curtain_wall_id(el):
    """
    Try a few robust ways to retrieve the parent curtain wall:
    1) Look for a parameter that stores the host wall id (common on panels/mullions).
    2) If the element exposes a Host with an OwnerId, use that.
    Returns ElementId or None.
    """
    # 1) Known parameter paths that often exist on panels/mullions
    bip_candidates = [
        getattr(BuiltInParameter, 'CURTAIN_WALL_ID', None),
        getattr(BuiltInParameter, 'HOST_ID_PARAM', None),
    ]
    for bip in [b for b in bip_candidates if b is not None]:
        p = el.get_Parameter(bip)
        if p and p.HasValue:
            try:
                host_id = p.AsElementId()
            except:
                host_id = None
            if host_id and host_id.IntegerValue > 0:
                host_el = doc.GetElement(host_id)
                # Accept if it's a curtain wall (or if Revit returns a valid element we can isolate)
                if isinstance(host_el, Wall):
                    wt = host_el.WallType
                    try:
                        is_curtain = wt.Kind.ToString() == 'Curtain'
                    except:
                        # Older API: Kind is an enum; compare by name safely
                        is_curtain = str(wt.Kind) == 'Curtain'
                    if is_curtain:
                        return host_id
                else:
                    # Some environments may return a CurtainSystem or similar—still usable for isolation
                    return host_id

    # 2) Some API surfaces expose Host with an OwnerId (e.g. a CurtainGrid host)
    host = getattr(el, 'Host', None)
    if host is not None:
        owner_id = getattr(host, 'OwnerId', None)
        if owner_id and isinstance(owner_id, ElementId) and owner_id.IntegerValue > 0:
            return owner_id

    return None

# Main function to list warnings and isolate elements
def prepare_warnings_for_isolation(doc, uidoc):
    # Retrieve all warnings
    warnings = doc.GetWarnings()
    unique_warnings = set()

    # Process warnings to get unique descriptions
    for warning in warnings:
        unique_warnings.add(warning.GetDescriptionText())

    # Display checklist form using pyRevit forms
    selected_warnings = forms.SelectFromList.show(
        sorted(unique_warnings),
        multiselect=True,
        button_name='Isolate Elements'
    )

    if selected_warnings:
        # Collect elements to isolate
        element_ids_to_isolate = set()
        for warning in warnings:
            if warning.GetDescriptionText() in selected_warnings:
                for fid in warning.GetFailingElements():
                    el = doc.GetElement(fid)
                    if el is None or el.Category is None:
                        # Fallback to whatever id we have
                        element_ids_to_isolate.add(fid)
                        continue

                    cat_int = el.Category.Id.IntegerValue
                    if _is_curtain_subcategory(cat_int):
                        host_wall_id = _get_host_curtain_wall_id(el)
                        if host_wall_id:
                            element_ids_to_isolate.add(host_wall_id)
                        else:
                            # If we can’t resolve the host for any reason, isolate the element itself
                            element_ids_to_isolate.add(fid)
                    else:
                        element_ids_to_isolate.add(fid)

        # Convert to ICollection[ElementId]
        element_ids = List[ElementId](element_ids_to_isolate)
        return element_ids
    return None

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝ MAIN
# ==================================================
with Transaction(doc, "Isolate Warnings") as trans:
    trans.Start()
    element_ids = prepare_warnings_for_isolation(doc, uidoc)
    if element_ids and element_ids.Count > 0:
        uidoc.ActiveView.IsolateElementsTemporary(element_ids)
    trans.Commit()

if element_ids:
    TaskDialog.Show("Isolation Complete", "Elements with the selected warnings have been isolated in the active view.")
else:
    TaskDialog.Show("Isolation Cancelled", "No warnings were selected for isolation.")

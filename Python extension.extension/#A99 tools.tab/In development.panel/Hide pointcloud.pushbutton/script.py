# -*- coding: utf-8 -*-
__title__ = "Hide Pointcloud \nin Active View"
__doc__ = """Version = 1.0
Date    = 09.01.2025
_____________________________________________________________________
Description:
Toggle visibility of all point clouds in the active view.
If at least one point cloud is visible, hides all point clouds.
If all point clouds are hidden, shows all point clouds.
Works with views controlled by view templates.
_____________________________________________________________________
Author: Jakub Dvořáček
"""

__author__ = "Jakub Dvořáček"
__helpurl__ = "https://atelier99cz.sharepoint.com/sites/Atelier99/SitePages/Main%20pages/BIM_Revit.aspx"

# ==================================================
# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, FilteredElementCollector
from pyrevit import script, forms

# ==================================================
# Revit context
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

# ==================================================
# Helpers
def get_point_clouds_in_view(doc, view):
    """
    Get all PointCloudInstance elements that can be hidden/shown in the view.
    Returns list of ElementIds.
    Important: We get ALL point clouds that exist, then filter by what we can actually hide/unhide.
    """
    all_point_clouds = FilteredElementCollector(doc)\
        .OfClass(PointCloudInstance)\
        .WhereElementIsNotElementType()\
        .ToElementIds()
    
    # For toggle to work, we need to track ALL point clouds that were ever hidden via HideElements
    # So we include all point clouds and let the hide/unhide operations handle validation
    valid_ids = []
    for pc_id in all_point_clouds:
        try:
            # Try to check if element can be hidden/unhidden
            # But don't exclude if CanElementBeHidden returns False - element might be already hidden
            if hasattr(view, 'CanElementBeHidden'):
                # Check if element can be hidden (when visible) OR if it's already hidden
                # If CanElementBeHidden returns False, try IsElementHidden to see if it's hidden
                can_hide = view.CanElementBeHidden(pc_id)
                is_hidden = False
                try:
                    is_hidden = view.IsElementHidden(pc_id)
                except:
                    pass
                
                # Include if can be hidden OR if already hidden (so we can unhide it)
                if can_hide or is_hidden:
                    valid_ids.append(pc_id)
            else:
                # Fallback: try IsElementHidden to verify element is accessible in view
                try:
                    view.IsElementHidden(pc_id)
                    valid_ids.append(pc_id)
                except Exception:
                    # If that fails, include anyway - let HideElements/UnhideElements handle it
                    valid_ids.append(pc_id)
        except Exception:
            # On error, include element anyway - better to try than skip
            valid_ids.append(pc_id)
    
    return valid_ids


def is_element_hidden_per_element(view, element_id):
    """
    Check if element is hidden via per-element hide (HideElements), not VG/Template.
    Returns True if hidden per-element, False if visible or hidden via other means.
    """
    try:
        # IsElementHidden returns True only if element was hidden via HideElements
        return view.IsElementHidden(element_id)
    except Exception:
        # If method fails, assume not hidden per-element
        return False


def get_hidden_status_robust(view, element_ids):
    """
    Check which elements are hidden via per-element hide in the view.
    Returns tuple: (list of booleans, list of valid element IDs)
    Important: We check ALL elements that were initially valid, even if they're currently hidden.
    """
    hidden_flags = []
    valid_ids = []
    
    for el_id in element_ids:
        try:
            # Check if hidden via per-element hide
            # Note: IsElementHidden can be called even on hidden elements
            is_hidden = is_element_hidden_per_element(view, el_id)
            hidden_flags.append(is_hidden)
            valid_ids.append(el_id)
        except Exception as e:
            # If we can't check, skip this element
            continue
    
    return hidden_flags, valid_ids


def hide_elements_in_view(view, element_ids):
    """
    Hide elements in the view using HideElements method.
    Returns True if successful, False otherwise.
    """
    if not element_ids:
        return False
    
    try:
        from System.Collections.Generic import List
        id_list = List[ElementId](element_ids)
        view.HideElements(id_list)
        return True
    except Exception as e:
        # Log error but don't fail completely
        return False


def unhide_elements_in_view(view, element_ids):
    """
    Unhide elements in the view using UnhideElements method.
    Returns tuple: (success: bool, error_message: str or None)
    Important: UnhideElements works even if elements are currently hidden.
    """
    if not element_ids:
        return False, None
    
    try:
        from System.Collections.Generic import List
        id_list = List[ElementId](element_ids)
        # UnhideElements should work even if CanElementBeHidden returns False for hidden elements
        view.UnhideElements(id_list)
        return True, None
    except Exception as e:
        # If UnhideElements fails, return error message for diagnostics
        error_msg = "UnhideElements failed: {}".format(str(e))
        return False, error_msg


def check_view_template_visibility(view):
    """
    Check if view has a template and if point clouds might be hidden via template/VG.
    Returns tuple: (has_template, template_name, warning_message)
    """
    try:
        if view.ViewTemplateId != ElementId.InvalidElementId:
            template_view = doc.GetElement(view.ViewTemplateId)
            if template_view:
                template_name = template_view.Name if hasattr(template_view, 'Name') else "Unknown"
                return True, template_name, None
        
        return False, None, None
    except Exception:
        return False, None, None


def verify_unhide_success(view, element_ids):
    """
    After unhide, verify that elements are actually visible.
    Returns tuple: (all_visible, hidden_count, warning_message)
    """
    still_hidden = []
    for el_id in element_ids:
        try:
            if view.IsElementHidden(el_id):
                still_hidden.append(el_id)
        except Exception:
            # Can't verify, assume OK
            pass
    
    if still_hidden:
        has_template, template_name, _ = check_view_template_visibility(view)
        if has_template:
            warning = "Mračna byla odskryta na úrovni prvků, ale pohled/šablona je stále skrývá přes VG/Template. Zkontroluj View Template '{}' / Visibility Graphics.".format(template_name)
        else:
            warning = "Některá mračna byla odskryta na úrovni prvků, ale stále nejsou viditelná. Zkontroluj Visibility Graphics v pohledu."
        return False, len(still_hidden), warning
    
    return True, 0, None


# ==================================================
# Main
if __name__ == '__main__':
    # Check if active view is valid
    active_view = doc.ActiveView
    if not active_view:
        forms.alert("Aktivní pohled není k dispozici.", exitscript=True)
    
    view_name = active_view.Name
    
    # Get all point clouds in the project
    point_cloud_ids = get_point_clouds_in_view(doc, active_view)
    
    # Check if any point clouds exist
    if not point_cloud_ids:
        forms.alert("V projektu nejsou žádná mračna bodů.", exitscript=True)
    
    # Get current hidden status - check ALL point clouds we found
    # This includes ones that might be currently hidden
    hidden_flags, valid_point_cloud_ids = get_hidden_status_robust(active_view, point_cloud_ids)
    
    # Check if we have any valid elements to toggle
    if not valid_point_cloud_ids:
        forms.alert("V aktivním pohledu nejsou žádná mračna bodů, která lze skrýt/zobrazit na úrovni prvků.\nMožná jsou skrytá přes View Template nebo Visibility Graphics.", exitscript=True)
    
    # Determine toggle action based on per-element hide status
    # If any is visible (not hidden per-element), hide all
    # If all are hidden per-element, show all
    # Important: Check actual hidden status using IsElementHidden
    any_visible = any(not h for h in hidden_flags) if hidden_flags else False
    
    # Perform the action
    t = Transaction(doc, __title__)
    t.Start()
    
    try:
        success = False
        if any_visible:
            # Hide all point clouds
            success = hide_elements_in_view(active_view, valid_point_cloud_ids)
            action_text = "skryta"
            affected_count = len(valid_point_cloud_ids)
        else:
            # Unhide all point clouds
            # Important: Only unhide elements that are actually hidden via HideElements
            hidden_ids = [el_id for el_id, is_hidden in zip(valid_point_cloud_ids, hidden_flags) if is_hidden]
            
            if not hidden_ids:
                # No elements are hidden via HideElements, so nothing to unhide
                t.RollBack()
                forms.alert("Žádná mračna bodů nejsou skrytá přes Hide Elements.\nMožná jsou skrytá přes View Template nebo Visibility Graphics.", exitscript=True)
            
            success, error_msg = unhide_elements_in_view(active_view, hidden_ids)
            action_text = "zobrazena"
            affected_count = len(hidden_ids)
            
            if not success:
                t.RollBack()
                if error_msg:
                    forms.alert("Chyba při zobrazování mračen bodů:\n{}".format(error_msg), exitscript=True)
                else:
                    forms.alert("Chyba při zobrazování mračen bodů.", exitscript=True)
        
        if not success:
            t.RollBack()
            forms.alert("Chyba při změně viditelnosti mračen bodů.", exitscript=True)
        
        t.Commit()
        
        # After unhide, verify that elements are actually visible
        warning_msg = None
        if not any_visible:  # We just unhid
            # Check only the elements we actually unhid
            hidden_ids = [el_id for el_id, is_hidden in zip(valid_point_cloud_ids, hidden_flags) if is_hidden]
            all_visible, hidden_count, warning = verify_unhide_success(active_view, hidden_ids)
            if warning:
                warning_msg = warning
        
        # Show success message
        message = "Mračna bodů byla {} v aktivním pohledu: {}\nPočet ovlivněných prvků: {}".format(
            action_text, view_name, affected_count
        )
        
        if warning_msg:
            message += "\n\n⚠️ " + warning_msg
        
        forms.alert(message)
        
    except Exception as e:
        t.RollBack()
        error_msg = "Chyba při změně viditelnosti mračen bodů:\n{}".format(str(e))
        forms.alert(error_msg, exitscript=True)

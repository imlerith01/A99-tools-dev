# -*- coding: utf-8 -*-
__title__ = "Room Code"
__doc__ = """Version = 1.6
Date    = 09.09.2025
_____________________________________________________________________
Description:
Builds a room code from four parameters in this order:
  Část objektu . Podlaží(number, zero-padded) . Obsazení . Číslo místnosti
Where "Podlaží" is in the form 1NP, 2NP, ..., 10NP, 11NP and gets converted to 01, 02, ..., 10, 11.
Writes the result into the parameter "Číslo" without pre-checks (missing/readonly/type).
Counts unplaced rooms as "Počet neumístěných místností".
_____________________________________________________________________
Author: Jakub Dvořáček
"""

__author__  = "Jakub Dvořáček"
__helpurl__ = "https://atelier99cz.sharepoint.com/sites/Atelier99/SitePages/Main%20pages/BIM_Revit.aspx"

# ==================================================
# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, FilteredElementCollector, BuiltInCategory
from pyrevit import script

# ==================================================
# Revit context
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application

# ==================================================
# Parameters
PARAM_OUT   = u"Číslo"
PARAM_PART  = u"Část objektu"
PARAM_LEVEL = u"Podlaží"
PARAM_OCC   = u"Obsazení"
PARAM_NUM   = u"Číslo místnosti"

DELIM = u"."

# ==================================================
# Helpers
def _get_param(elem, name):
    if not elem:
        return None
    try:
        return elem.LookupParameter(name)
    except Exception:
        return None

def _get_param_str(elem, name):
    p = _get_param(elem, name)
    if not p:
        return None
    try:
        val = p.AsString()
        if val is None:
            val = p.AsValueString()
    except Exception:
        val = None
    if val is None:
        return None
    val = val.strip()
    return val if val else None

def _room_area_gt_zero(room):
    try:
        return float(room.Area or 0.0) > 0.0
    except Exception:
        return False

def _parse_level_number(level_name):
    """Expects Podlaží like '1NP', '2NP', '10NP', ... and returns '01', '02', '10', ..."""
    if not level_name or len(level_name) < 3:
        return None
    try:
        num_part = level_name[:-2]  # strip 'NP'
        num_int = int(num_part)
        return "{:02d}".format(num_int)
    except Exception:
        return None

# ==================================================
# Main
output = script.get_output()

processed = 0
errors = 0
skipped_unplaced = 0
skipped_missing_inputs = 0

rooms = FilteredElementCollector(doc)\
    .OfCategory(BuiltInCategory.OST_Rooms)\
    .WhereElementIsNotElementType()\
    .ToElements()

t = Transaction(doc, __title__)
t.Start()

try:
    for room in rooms:
        # Count unplaced (area <= 0) as "neumístěné" and skip
        if not _room_area_gt_zero(room):
            skipped_unplaced += 1
            continue

        # Read inputs
        part = _get_param_str(room, PARAM_PART)     # Část objektu
        level_raw = _get_param_str(room, PARAM_LEVEL)  # Podlaží (e.g., 1NP)
        occ  = _get_param_str(room, PARAM_OCC)      # Obsazení
        num  = _get_param_str(room, PARAM_NUM)      # Číslo místnosti

        if not (part and level_raw and occ and num):
            skipped_missing_inputs += 1
            continue

        # Convert level to zero-padded number
        level_code = _parse_level_number(level_raw)
        if not level_code:
            skipped_missing_inputs += 1
            continue

        # Build final value
        value = u"{part}{d}{lvl}{d}{occ}{d}{num}".format(
            part=part, lvl=level_code, occ=occ, num=num, d=DELIM
        )

        # Try writing to "Číslo" without any pre-checks (missing/readonly/type)
        try:
            p_out = _get_param(room, PARAM_OUT)
            # This can fail if p_out is None, readonly, or wrong type — that's intended per request.
            p_out.Set(value)
            processed += 1
        except Exception as ex:
            errors += 1
            print(u"[CHYBA] Nelze zapsat do místnosti ID {}: {}".format(room.Id.IntegerValue, ex))

finally:
    t.Commit()

total = len(rooms)
skipped_total = total - processed

print(u"Hotovo ({})".format(__title__))
print(u"Zpracováno: {} | Přeskočeno: {} | Chyby: {}".format(processed, skipped_total, errors))
print(u"- Počet neumístěných místností: {}".format(skipped_unplaced))
print(u"- Chybějící vstupní parametry (vč. neplatného Podlaží): {}".format(skipped_missing_inputs))

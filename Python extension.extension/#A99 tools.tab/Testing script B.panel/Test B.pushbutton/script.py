# -*- coding: utf-8 -*-
__title__ = "Room Code Builder"
__doc__ = """Version = 1.8
Date    = 09.09.2025
_____________________________________________________________________
Description:
Builds a room code from four parameters in this order:
  Část objektu . Podlaží(number, zero-padded) . Obsazení . Číslo místnosti
"Podlaží" may look like 1NP, 1.NP, 10NP, 10.NP, etc. -> becomes 01, 10, ...
Writes the result into the parameter "Číslo" without pre-checks.
Counts unplaced rooms as "Počet neumístěných místností".
Adds a clickable report of all skipped rooms (name, level, ID, missing parameter).
_____________________________________________________________________
Author: Jakub Dvořáček
"""

__author__  = "Jakub Dvořáček"
__helpurl__ = "https://atelier99cz.sharepoint.com/sites/Atelier99/SitePages/Main%20pages/BIM_Revit.aspx"

# ==================================================
# Imports
import re
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, FilteredElementCollector, BuiltInCategory
from pyrevit import script

# ==================================================
# Revit context
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application
output = script.get_output()

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
    """
    Accepts '1NP', '1.NP', '10NP', '10.NP', etc.
    Returns '01', '10', ... (zero-padded to 2).
    """
    if not level_name:
        return None
    m = re.search(r'\d+', level_name)
    if not m:
        return None
    try:
        num_int = int(m.group(0))
        return "{:02d}".format(num_int)
    except Exception:
        return None

def _room_name(room):
    try:
        return room.Parameter[BuiltInParameter.ROOM_NAME].AsString() or u"(bez názvu)"
    except:
        return u"(bez názvu)"

def _room_level_name(room):
    # Prefer actual Level element
    try:
        lev = doc.GetElement(room.LevelId)
        if lev and hasattr(lev, "Name") and lev.Name:
            return lev.Name
    except:
        pass
    # Fallback to custom parameter "Podlaží"
    return _get_param_str(room, PARAM_LEVEL) or u"(neznámé podlaží)"

# ==================================================
# Main
processed = 0
errors = 0
skipped_unplaced = 0
skipped_missing_inputs = 0

# Collect detailed info for skipped rooms
skipped_details = []   # each item: dict(name, level, id, reason)

rooms = FilteredElementCollector(doc)\
    .OfCategory(BuiltInCategory.OST_Rooms)\
    .WhereElementIsNotElementType()\
    .ToElements()

t = Transaction(doc, __title__)
t.Start()

try:
    for room in rooms:
        # Unplaced (area <= 0)
        if not _room_area_gt_zero(room):
            skipped_unplaced += 1
            skipped_details.append(dict(
                name=_room_name(room),
                level=_room_level_name(room),
                id=room.Id,
                reason=u"Neumístěná (plocha ≤ 0)"
            ))
            continue

        # Read inputs
        part = _get_param_str(room, PARAM_PART)       # Část objektu
        level_raw = _get_param_str(room, PARAM_LEVEL) # Podlaží (e.g., 1.NP, 2NP)
        occ  = _get_param_str(room, PARAM_OCC)        # Obsazení
        num  = _get_param_str(room, PARAM_NUM)        # Číslo místnosti

        # Check which inputs are missing
        missing = []
        if not part:      missing.append(PARAM_PART)
        if not level_raw: missing.append(PARAM_LEVEL)
        if not occ:       missing.append(PARAM_OCC)
        if not num:       missing.append(PARAM_NUM)

        # Parse level code
        level_code = _parse_level_number(level_raw) if level_raw else None
        if level_raw and not level_code:
            missing.append(u"Podlaží (neplatný formát)")

        if missing:
            skipped_missing_inputs += 1
            skipped_details.append(dict(
                name=_room_name(room),
                level=_room_level_name(room),
                id=room.Id,
                reason=u", ".join(missing)
            ))
            continue

        # Build final value
        value = u"{part}{d}{lvl}{d}{occ}{d}{num}".format(
            part=part, lvl=level_code, occ=occ, num=num, d=DELIM
        )

        # Write to "Číslo" without pre-checks (per your preference)
        try:
            p_out = _get_param(room, PARAM_OUT)
            p_out.Set(value)  # may fail if None/readonly/wrong type
            processed += 1
        except Exception as ex:
            errors += 1
            skipped_details.append(dict(
                name=_room_name(room),
                level=_room_level_name(room),
                id=room.Id,
                reason=u"Zápis do 'Číslo' selhal: {}".format(ex)
            ))

finally:
    t.Commit()

total = len(rooms)
skipped_total = total - processed

# =======================
# Summary
print(u"Hotovo ({})".format(__title__))
print(u"Zpracováno: {} | Přeskočeno: {} | Chyby: {}".format(processed, skipped_total, errors))
print(u"- Počet neumístěných místností: {}".format(skipped_unplaced))
print(u"- Chybějící/Neplatné vstupní parametry: {}".format(skipped_missing_inputs))

# =======================
# Clickable list of all skipped rooms
if skipped_details:
    print(u"\nSeznam přeskočených místností (kliknutím vyberete v Revit):")
    print(u"ID; Název; Podlaží; Důvod")
    print(u"----------------------------------------------")
    for item in skipped_details:
        link = output.linkify(item["id"])
        print(u"{id}; {name}; {lvl}; {reason}".format(
            id=link,
            name=item["name"],
            lvl=item["level"],
            reason=item["reason"]
        ))
else:
    print(u"\nŽádné přeskočené místnosti. 🎉")

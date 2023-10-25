# -*- coding: utf-8 -*-

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import (FilteredElementCollector, BuiltInCategory, JoinGeometryUtils,
                               Outline, BoundingBoxIntersectsFilter, Transaction)
from Autodesk.Revit.UI import TaskDialog

# Import pyRevit forms
from pyrevit import forms

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# Display the initial message to the user
TaskDialog.Show('Upozornění', 'Před spuštěním doplňku nejprve ulož model')


categories_dict = {
    "Stěny": BuiltInCategory.OST_Walls,
    "Podlahy": BuiltInCategory.OST_Floors,
    "Podhledy": BuiltInCategory.OST_Ceilings,
    "Střechy": BuiltInCategory.OST_Roofs,
    "Konstrukční sloupy": BuiltInCategory.OST_StructuralColumns,
    "Kontrukční rámové konstrukce": BuiltInCategory.OST_StructuralFraming
}

def join_intersecting_elements(selected_categories):
    join_count = 0
    t = Transaction(doc, 'Join Intersecting Elements')
    t.Start()

    elements = []
    for category in selected_categories:
        elements.extend(FilteredElementCollector(doc, uidoc.ActiveView.Id).OfCategory(category).WhereElementIsNotElementType().ToElements())

    selected_category_ids = [doc.Settings.Categories.get_Item(cat).Id for cat in selected_categories]

    for elem in elements:
        outline = Outline(elem.BoundingBox[uidoc.ActiveView].Min, elem.BoundingBox[uidoc.ActiveView].Max)
        bbFilter = BoundingBoxIntersectsFilter(outline)
        intersecting_elements = FilteredElementCollector(doc, uidoc.ActiveView.Id).WherePasses(bbFilter).ToElements()
        for other_elem in intersecting_elements:
            if other_elem.Category.Id in selected_category_ids and elem.Id != other_elem.Id and not JoinGeometryUtils.AreElementsJoined(doc, elem, other_elem):
                try:
                    JoinGeometryUtils.JoinGeometry(doc, elem, other_elem)
                    join_count += 1
                except:
                    pass

    t.Commit()
    return join_count

# Use pyRevit forms for category selection
selected_categories = forms.SelectFromList.show(sorted(categories_dict.keys()), multiselect=True, title="Vyberte kategorie k spojení")

if selected_categories:
    selected_categories = [categories_dict[cat] for cat in selected_categories]
    joined_elements_count = join_intersecting_elements(selected_categories)
    TaskDialog.Show('Info', '{} prvků bylo úspěšně spojeno.'.format(joined_elements_count))

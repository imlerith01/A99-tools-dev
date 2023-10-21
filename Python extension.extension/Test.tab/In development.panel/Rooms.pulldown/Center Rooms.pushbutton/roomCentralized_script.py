__doc__ = "Move the room placement point to the center of its geometry. "\
		"It might work differently for non-rectangular rooms."

import math
from pyrevit import script, revit, DB
from pyrevit import forms

doc = revit.doc
uidoc = revit.uidoc
BIC = DB.BuiltInCategory

def float_range(start, end, nr):
	nr = int(nr)
	increment = float(end-start)/int(nr-1)
	for i in range(nr):
		yield	start + increment*i

def get_centerPoint(room):
	bb = room.get_BoundingBox(None)
	pt = DB.Line.CreateBound(bb.Min, bb.Max).Evaluate(0.5, True)
	if room.IsPointInRoom(pt):
		return	pt
	else:
		ratio = math.fabs(bb.Min.Y-bb.Max.Y) / math.fabs(bb.Min.X-bb.Max.X)
		for divisions in range(5, 10):
			xs = list(float_range(bb.Min.X, bb.Max.X, divisions))
			ys = list(float_range(bb.Min.Y, bb.Max.Y, divisions*ratio))
			for x in xs[1:-1]:
				for y in ys[1:-1]:
					pt = DB.XYZ(x, y, pt.Z)
					if room.IsPointInRoom(pt):
						return	pt

# UI CHOOSE THE OPTION
context = ['All rooms in active view', 'Select Rooms', 'All placed rooms in the project']
user_input = forms.CommandSwitchWindow.show(context)

# SELECT ROOMS
if user_input:
	if user_input == context[0]:
		rooms = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(BIC.OST_Rooms).WhereElementIsNotElementType().ToElements()
	elif user_input == context[1]:
		with forms.WarningBar(title='Pick rooms to centralize'):
			rooms = revit.pick_elements_by_category(BIC.OST_Rooms)
	elif user_input == context[2]:
		rooms = DB.FilteredElementCollector(doc).OfCategory(BIC.OST_Rooms).WhereElementIsNotElementType().ToElements()
		rooms = [room for room in rooms if room.Location is not None]  # Exclude unplaced rooms

	# MOVE LOCATION POINTS
	if rooms:
		print 'LIST OF MOVED ROOMS:\n(starting point)\n(ending point)'
		with revit.Transaction('Centralize Rooms'):
			for room in rooms:
				print '---\n{} - {}'.format(room.Number, DB.Element.Name.__get__(room))
				print	room.Location.Point
				if get_centerPoint(room):
					room.Location.Point = get_centerPoint(room)
					print	room.Location.Point
				else:
					print	'NOT MOVED'

	uidoc.RefreshActiveView()
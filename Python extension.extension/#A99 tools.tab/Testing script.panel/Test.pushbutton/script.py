import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ElementId, Transaction
from Autodesk.Revit.UI import TaskDialog
from System.Windows.Forms import Application, Form, CheckedListBox, Button, DialogResult
from System.Drawing import Size

# Class to create a checklist form
class ChecklistForm(Form):
    def __init__(self, items):
        self.checkedItems = []
        self.InitializeComponent(items)

    def InitializeComponent(self, items):
        self.checkedListBox = CheckedListBox()
        self.checkedListBox.Items.AddRange(items)
        self.checkedListBox.CheckOnClick = True
        self.checkedListBox.Size = Size(300, 200)

        self.button = Button()
        self.button.Text = 'OK'
        self.button.Click += self.button_click
        self.button.Location = System.Drawing.Point(100, 210)

        self.Controls.Add(self.checkedListBox)
        self.Controls.Add(self.button)
        self.Size = Size(320, 260)

    def button_click(self, sender, e):
        self.checkedItems = [self.checkedListBox.Items[i] for i in range(self.checkedListBox.Items.Count) if self.checkedListBox.GetItemChecked(i)]
        self.DialogResult = DialogResult.OK

# Main function to list warnings and isolate elements
def isolate_warnings_elements(doc, uidoc):
    # Retrieve all warnings
    warnings = doc.GetWarnings()
    unique_warnings = set()

    # Process warnings to get unique descriptions
    for warning in warnings:
        unique_warnings.add(warning.GetDescriptionText())

    # Display checklist form
    form = ChecklistForm(list(unique_warnings))
    Application.EnableVisualStyles()
    result = form.ShowDialog()

    if result == DialogResult.OK:
        selected_warnings = form.checkedItems

        # Collect elements to isolate
        elements_to_isolate = set()
        for warning in warnings:
            if warning.GetDescriptionText() in selected_warnings:
                elements_to_isolate.update(warning.GetFailingElements())

        # Convert to ElementId set
        element_ids = [ElementId(id) for id in elements_to_isolate]

        # Start a transaction to modify the document
        with Transaction(doc, "Isolate Warnings") as trans:
            trans.Start()
            view = uidoc.ActiveView
            view.IsolateElementsTemporary(element_ids)
            trans.Commit()

        TaskDialog.Show("Isolation Complete", "Elements with the selected warnings have been isolated in the active view.")

# Boilerplate code
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

isolate_warnings_elements(doc, uidoc)

# -*- coding: utf-8 -*-
# pylint: disable=E0401,W0613,C0103,C0111
import sys
from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms

# Setting up the logger for the script.
logger = script.get_logger()


# Handler for duplicate type names during the copy process.
class CopyUseDestination(DB.IDuplicateTypeNamesHandler):
    def OnDuplicateTypeNamesFound(self, args):
        # If duplicate type names are found, use the type names from the destination document.
        return DB.DuplicateTypeAction.UseDestinationTypes


# Prompt the user to select destination documents excluding the current active one.
open_docs = forms.select_open_docs(title='Select Destination Documents')
# Exit the script if no documents are selected.
if not open_docs:
    sys.exit(0)

# Prompt the user to select drafting views of type 'Legend'.
# If any views are pre-selected in Revit, those will be used.
legends = forms.select_views(
    title='Select Drafting Views',
    filterfunc=lambda x: x.ViewType == DB.ViewType.Legend,
    use_selection=True)

# If any legends are selected, begin the copying process.
if legends:
    for dest_doc in open_docs:
        # Retrieve all views in the destination document and their names.
        all_graphviews = revit.query.get_all_views(doc=dest_doc)
        all_legend_names = [revit.query.get_name(x) for x in all_graphviews if x.ViewType == DB.ViewType.Legend]

        print('Processing Document: {0}'.format(dest_doc.Title))

        # Find the first legend view in the destination document.
        base_legend = revit.query.find_first_legend(doc=dest_doc)
        # If no legend exists in the destination document, alert the user and exit.
        if not base_legend:
            forms.alert('At least one Legend must exist in target document.', exitscript=True)

        # Iterate over each source legend view.
        for src_legend in legends:
            print('\tCopying: {0}'.format(revit.query.get_name(src_legend)))

            # Retrieve all elements inside the source legend view.
            view_elements = DB.FilteredElementCollector(revit.doc, src_legend.Id).ToElements()

            # Filter out elements that can't be copied.
            elements_to_copy = [el.Id for el in view_elements if isinstance(el, DB.Element) and el.Category]
            if not elements_to_copy:
                logger.debug('Skipping empty view: %s', revit.query.get_name(src_legend))
                continue

            # Begin transaction to copy the legend to the destination document.
            with revit.Transaction('Copy Legends to this document', doc=dest_doc):
                # Duplicate the base legend in the destination document.
                dest_view = dest_doc.GetElement(base_legend.Duplicate(DB.ViewDuplicateOption.Duplicate))

                # Setup the copy options and handle duplicate type names.
                options = DB.CopyPasteOptions()
                options.SetDuplicateTypeNamesHandler(CopyUseDestination())
                copied_elements = DB.ElementTransformUtils.CopyElements(
                    src_legend, List[DB.ElementId](elements_to_copy), dest_view, None, options
                )

                # Match graphical overrides of the copied elements to the source.
                for dest, src in zip(copied_elements, elements_to_copy):
                    dest_view.SetElementOverrides(dest, src_legend.GetElementOverrides(src))

                # Ensure the copied legend's name is unique. If not, rename it.
                src_name = revit.query.get_name(src_legend)
                count = 0
                new_name

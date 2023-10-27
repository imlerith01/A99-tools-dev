# -*- coding: utf-8 -*-
"""Non-exhaustive check to detect corrupt Revit families."""
# Import necessary libraries and handle pylint specific warnings
#pylint: disable=invalid-name,import-error,superfluous-parens,broad-except
from pyrevit import revit, forms, script

# Initialize the logger and output for the script
logger = script.get_logger()
output = script.get_output()

# Initialize counters for statistics
checked_families = 0
count_exceptions = 0
count_swallowed = 0
count_families_with_warnings = 0

# Get all families from the current document that are editable
all_families = revit.query.get_families(revit.doc, only_editable=True)
editable_families = []

# Check for a special "Shift + Click" event to allow user to select specific families
if __shiftclick__:
    family_dict = {}
    for family in all_families:
        if family.FamilyCategory:
            family_dict[
                "%s: %s" % (family.FamilyCategory.Name, family.Name)
            ] = family

    # Display a list for the user to select which families to check
    selected_families = forms.SelectFromList.show(
        sorted(family_dict.keys()),
        title="Select Families to Check",
        multiselect=True
    )
    if selected_families:
        editable_families = [family_dict[x] for x in selected_families]
else:
    # If no selection was made, consider all editable families
    editable_families = [x for x in all_families if x.IsEditable]

# Store the total count of families to be checked
total_count = len(editable_families)

# Reset the output progress bar
output.reset_progress()

# Begin checking families for errors
with revit.ErrorSwallower(log_errors=True) as swallower:
    for fam in editable_families:
        fam_name = revit.query.get_name(fam)
        logger.debug("attempt to open family: %s", fam_name)

        try:
            # Try opening the family to see if it's corrupt
            fam_doc = revit.doc.EditFamily(fam)
            swallowed_errors = swallower.get_swallowed_errors()

            # Report any swallowed warnings from the family
            if swallowed_errors:
                error_descs = "\n".join(
                    [x.GetDescriptionText() for x in swallowed_errors]
                )
                logger.warning(":warning: %s\n%s", fam.Name, error_descs)
                count_swallowed += len(swallowed_errors)
                count_families_with_warnings += 1
            else:
                print(":white_heavy_check_mark: %s" % fam_name)

            # Close the family after checking
            fam_doc.Close(False)
            swallower.reset()

        except Exception as ex:
            # If an exception occurs, log it and increment the counter
            logger.error(":cross_mark: %s | error: %s", fam.Name, ex)
            count_exceptions += 1

        # Update progress and proceed to the next family
        checked_families += 1
        output.update_progress(checked_families, total_count)
        output.set_title("Family QuickCheck (X{} !{})"
                         .format(count_exceptions, count_swallowed))
        if output.is_closed_by_user:
            script.exit()

# Display results
print("\nChecked: {} families.".format(checked_families))

if count_exceptions:
    logger.warning("%s families seem to be corrupted", count_exceptions)

if count_families_with_warnings and count_swallowed:
    logger.warning(
        "%s families have total of %s warnings",
        count_families_with_warnings,
        count_swallowed
    )

if not (count_exceptions and count_swallowed):
    logger.success("Finished. No errors found.")

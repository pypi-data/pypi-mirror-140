from nautilus_librarian.mods.dvc.domain.utils import (
    extract_all_added_and_modified_and_renamed_files_from_dvc_diff,
    get_new_filepath_if_is_a_renaming_dict,
)
from nautilus_librarian.mods.namecodes.domain.validate_filenames import (
    validate_filename,
)
from nautilus_librarian.typer.commands.workflows.actions.action_result import (
    ActionResult,
    ErrorMessage,
    Message,
    ResultCode,
)


def validate_filenames(dvc_diff):
    """
    It validates all the filenames in the dvc diff.
    """
    if dvc_diff == "{}":
        return ActionResult(
            ResultCode.EXIT, [Message("No filenames to validate, empty DVC diff")]
        )

    # TODO: we have to review this function if we add files to DVC which do not belong to a media library.

    filenames = extract_all_added_and_modified_and_renamed_files_from_dvc_diff(dvc_diff)

    messages = []

    for filename in filenames:
        try:
            extracted_filename = get_new_filepath_if_is_a_renaming_dict(filename)
            validate_filename(extracted_filename)
            messages.append(Message(f"{extracted_filename} ✓"))
        except ValueError as error:
            return ActionResult(
                ResultCode.ABORT, [ErrorMessage(f"{filename} ✗ {error}")]
            )

    return ActionResult(ResultCode.CONTINUE, messages)

import json

from nautilus_librarian.mods.dvc.domain.dvc_diff_parser import DvcDiffParser


def test_dvc_diff_parser_initialization():

    dvc_diff = DvcDiffParser(
        {
            "added": [],
            "deleted": [],
            "modified": [],
            "renamed": [],
        }
    )

    assert isinstance(dvc_diff, DvcDiffParser)


def test_dvc_diff_parser_instantiation_from_json():

    dvc_diff_dict = {
        "added": [],
        "deleted": [],
        "modified": [],
        "renamed": [],
    }

    dvc_diff = DvcDiffParser.from_json(json.dumps(dvc_diff_dict))

    assert isinstance(dvc_diff, DvcDiffParser)


def it_should_get_the_added_files():

    dvc_diff = DvcDiffParser(
        {
            "added": [
                {"path": "folder/added_file.txt"},
            ],
            "deleted": [],
            "modified": [],
            "renamed": [],
        }
    )

    added = dvc_diff.added()

    assert added == ["folder/added_file.txt"]


def it_should_get_only_the_basenames_of_the_added_files():

    dvc_diff = DvcDiffParser(
        {
            "added": [
                {"path": "folder/added_file.txt"},
            ],
            "deleted": [],
            "modified": [],
            "renamed": [],
        }
    )

    added = dvc_diff.added(only_basename=True)

    assert added == ["added_file.txt"]


def it_should_get_the_deleted_files():

    dvc_diff = DvcDiffParser(
        {
            "added": [],
            "deleted": [
                {"path": "folder/deleted_file.txt"},
            ],
            "modified": [],
            "renamed": [],
        }
    )

    added = dvc_diff.deleted()

    assert added == ["folder/deleted_file.txt"]


def it_should_get_only_the_basenames_of_the_deleted_files():

    dvc_diff = DvcDiffParser(
        {
            "added": [],
            "deleted": [
                {"path": "folder/deleted_file.txt"},
            ],
            "modified": [],
            "renamed": [],
        }
    )

    added = dvc_diff.deleted(only_basename=True)

    assert added == ["deleted_file.txt"]


def it_should_get_the_modified_files():

    dvc_diff = DvcDiffParser(
        {
            "added": [],
            "deleted": [],
            "modified": [
                {"path": "folder/modified_file.txt"},
            ],
            "renamed": [],
        }
    )

    added = dvc_diff.modified()

    assert added == ["folder/modified_file.txt"]


def it_should_get_only_the_basenames_of_the_modified_files():

    dvc_diff = DvcDiffParser(
        {
            "added": [],
            "deleted": [],
            "modified": [
                {"path": "folder/modified_file.txt"},
            ],
            "renamed": [],
        }
    )

    added = dvc_diff.modified(only_basename=True)

    assert added == ["modified_file.txt"]


def it_should_get_the_renamed_files():

    dvc_diff = DvcDiffParser(
        {
            "added": [],
            "deleted": [],
            "modified": [],
            "renamed": [
                {
                    "path": {
                        "old": "data/000001/32/000001-32.600.2.tif",
                        "new": "data/000002/32/000002-32.600.2.tif",
                    }
                },
                {
                    "path": {
                        "old": "data/000003/32/000003-32.600.2.tif",
                        "new": "data/000004/32/000004-32.600.2.tif",
                    }
                },
            ],
        }
    )

    renamed = dvc_diff.renamed()

    assert renamed == [
        {
            "old": "data/000001/32/000001-32.600.2.tif",
            "new": "data/000002/32/000002-32.600.2.tif",
        },
        {
            "old": "data/000003/32/000003-32.600.2.tif",
            "new": "data/000004/32/000004-32.600.2.tif",
        },
    ]


def it_should_get_only_the_basenames_of_the_renamed_files():

    dvc_diff = DvcDiffParser(
        {
            "added": [],
            "deleted": [],
            "modified": [],
            "renamed": [
                {
                    "path": {
                        "old": "folder/original_file.txt",
                        "new": "folder/renamed_file.txt",
                    }
                },
            ],
        }
    )

    added = dvc_diff.renamed(only_basename=True)

    assert added == [{"old": "original_file.txt", "new": "renamed_file.txt"}]


def it_should_filter_by_type_of_change():

    dvc_diff = DvcDiffParser(
        {
            "added": [
                {"path": "folder/added_file.txt"},
            ],
            "deleted": [
                {"path": "folder/deleted_file.txt"},
            ],
            "modified": [
                {"path": "folder/modified_file.txt"},
            ],
            "renamed": [
                {"path": "folder/renamed_file.txt"},
            ],
        }
    )

    assert dvc_diff.filter() == [
        "folder/added_file.txt",
        "folder/deleted_file.txt",
        "folder/modified_file.txt",
        "folder/renamed_file.txt",
    ]

    assert dvc_diff.filter(exclude_added=True) == [
        "folder/deleted_file.txt",
        "folder/modified_file.txt",
        "folder/renamed_file.txt",
    ]

    assert dvc_diff.filter(exclude_deleted=True) == [
        "folder/added_file.txt",
        "folder/modified_file.txt",
        "folder/renamed_file.txt",
    ]

    assert dvc_diff.filter(exclude_modified=True) == [
        "folder/added_file.txt",
        "folder/deleted_file.txt",
        "folder/renamed_file.txt",
    ]

    assert dvc_diff.filter(exclude_renamed=True) == [
        "folder/added_file.txt",
        "folder/deleted_file.txt",
        "folder/modified_file.txt",
    ]

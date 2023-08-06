import json
import os


class DvcDiffParser:
    def __init__(self, dvc_diff: dict) -> None:
        self.dvc_diff = dvc_diff
        self.added_list = None
        self.deleted_list = None
        self.modified_list = None
        self.renamed_list = None
        self.parse()

    @staticmethod
    def from_json(dvc_diff):
        return DvcDiffParser(json.loads(dvc_diff))

    def parse(self):
        self.added_list = [element["path"] for element in self.dvc_diff["added"]]
        self.deleted_list = [element["path"] for element in self.dvc_diff["deleted"]]
        self.modified_list = [element["path"] for element in self.dvc_diff["modified"]]
        self.renamed_list = [element["path"] for element in self.dvc_diff["renamed"]]

    def basename_of(self, filepath: str) -> str:
        return os.path.basename(filepath)

    def basenames_of(self, filepaths: list[str]) -> list[str]:
        return [self.basename_of(filepath) for filepath in filepaths]

    def basenames_of_old_and_new(self, filepaths: list[dict]) -> list[dict]:
        return [
            {
                "new": self.basename_of(filepath_dict["new"]),
                "old": self.basename_of(filepath_dict["old"]),
            }
            for filepath_dict in filepaths
        ]

    def added(self, only_basename=False):
        if only_basename:
            return self.basenames_of(self.added_list)

        return self.added_list

    def deleted(self, only_basename=False):
        if only_basename:
            return self.basenames_of(self.deleted_list)

        return self.deleted_list

    def modified(self, only_basename=False):
        if only_basename:
            return self.basenames_of(self.modified_list)

        return self.modified_list

    def renamed(self, only_basename=False):
        if only_basename:
            return self.basenames_of_old_and_new(self.renamed_list)

        return self.renamed_list

    def filter(
        self,
        exclude_added=False,
        exclude_deleted=False,
        exclude_modified=False,
        exclude_renamed=False,
        only_basename=False,
    ):
        files = []

        if not exclude_added:
            files = files + self.added_list

        if not exclude_deleted:
            files = files + self.deleted_list

        if not exclude_modified:
            files = files + self.modified_list

        if only_basename:
            files = self.basenames_of(files)

        if not exclude_renamed:
            if only_basename:
                files = files + self.basenames_of_old_and_new(self.renamed_list)
            else:
                files = files + self.renamed_list

        return files

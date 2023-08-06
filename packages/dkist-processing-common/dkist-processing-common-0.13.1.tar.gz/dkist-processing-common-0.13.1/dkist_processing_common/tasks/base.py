"""
Wrappers for all workflow tasks
"""
import json
import logging
from abc import ABC
from io import BytesIO
from pathlib import Path
from typing import Generator
from typing import Iterable
from typing import List
from typing import Type
from typing import Union
from uuid import uuid4

import pkg_resources
from dkist_processing_core import TaskBase

from dkist_processing_common._util.config import get_config
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.constants import ConstantsBase
from dkist_processing_common.tasks.mixin.metadata_store import MetadataStoreMixin

__all__ = ["WorkflowTaskBase"]

logger = logging.getLogger(__name__)

tag_type_hint = Union[Iterable[str], str]


class WorkflowTaskBase(TaskBase, MetadataStoreMixin, ABC):
    """
    Wrapper for all tasks that need to access the persistent automated processing data stores.

    Adds capabilities for accessing:

    `scratch`
    `tags`
    `constants`

    Also includes ability to access the metadata store
    """

    is_task_manual: bool = False
    record_provenance: bool = False

    def __init__(
        self,
        recipe_run_id: int,
        workflow_name: str,
        workflow_version: str,
    ):
        super().__init__(
            recipe_run_id=recipe_run_id,
            workflow_name=workflow_name,
            workflow_version=workflow_version,
        )
        self.task_name = self.__class__.__name__
        self.scratch = WorkflowFileSystem(recipe_run_id=recipe_run_id, task_name=self.task_name)
        self.constants = self.constants_model_class(
            recipe_run_id=recipe_run_id, task_name=self.task_name
        )
        self.docs_base_url = get_config("DOCS_BASE_URL", "my_test_url")

    @property
    def constants_model_class(self) -> Type[ConstantsBase]:
        """
        The class containing the definitions of pipeline constants
        """
        return ConstantsBase

    @property
    def library_versions(self) -> str:
        """
        Harvest the dependency names and versions from the environment for
          all packages beginning with 'dkist' or are a requirement for a package
          beginning with 'dkist'
        """
        distributions = {d.key: d.version for d in pkg_resources.working_set}
        libraries = {}
        for pkg in pkg_resources.working_set:
            if pkg.key.startswith("dkist"):
                libraries[pkg.key] = pkg.version
                for req in pkg.requires():
                    libraries[req.key] = distributions[req.key]
        return json.dumps(libraries)

    def _record_provenance(self):
        logger.info(
            f"Recording provenance for {self.task_name}: "
            f"recipe_run_id={self.recipe_run_id}, "
            f"is_task_manual={self.is_task_manual}, "
            f"library_versions={self.library_versions}"
        )
        self.metadata_store_record_provenance(
            is_task_manual=self.is_task_manual, library_versions=self.library_versions
        )

    def pre_run(self) -> None:
        super().pre_run()
        if self.record_provenance:
            with self.apm_step("Record Provenance"):
                self._record_provenance()

    def read(self, tags: tag_type_hint) -> Generator[Path, None, None]:
        tags = self._parse_tags(tags)
        return self.scratch.find_all(tags=tags)

    def write(
        self,
        file_obj: Union[BytesIO, bytes],
        tags: tag_type_hint,
        relative_path: Union[Path, str, None] = None,
    ) -> Path:
        if isinstance(file_obj, BytesIO):
            file_obj = file_obj.read()
        tags = self._parse_tags(tags)
        relative_path = relative_path or f"{uuid4().hex}.dat"
        relative_path = Path(relative_path)
        self.scratch.write(file_obj=file_obj, relative_path=relative_path, tags=tags)
        return relative_path

    def count(self, tags: tag_type_hint) -> int:
        tags = self._parse_tags(tags)
        return self.scratch.count_all(tags=tags)

    def tag(self, path: Union[Path, str], tags: tag_type_hint) -> None:
        """
        Wrapper for the tag method in WorkflowFileSystem
        """
        tags = self._parse_tags(tags)
        return self.scratch.tag(path=path, tags=tags)

    def tags(self, path: Union[Path, str]) -> List[str]:
        """
        Return list of tags that a path belongs to
        """
        return self.scratch.tags(path=path)

    @staticmethod
    def _parse_tags(tags: tag_type_hint) -> Iterable[str]:
        result = []
        if isinstance(tags, str):
            tags = [tags]
        for tag in tags:
            if not isinstance(tag, str):
                raise TypeError(f"Tags must be strings. Got {type(tag)} instead.")
            result.append(tag)
        return result

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.scratch.close()
        self.constants._close()

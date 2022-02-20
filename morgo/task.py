from typing import List, Optional, Set, TypeVar

import pydantic

from morgo.exceptions import FrozenPropertyException, TaskMissingParameterException


class TaskConfig(pydantic.BaseModel):
    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class TaskParams(pydantic.BaseModel):
    pass


TaskType = TypeVar("Task")


class BaseTask:
    def _set_parameters(
        self, kwargs, annotations, params: Optional[TaskParams] = None
    ) -> TaskParams:
        """
        Sets the parameter attributes on a task looking at the Class's annotations.

        Note: This mutates self and will set all the params on self as well as _parameters.

        Args:
            kwargs (dict[str,Any]): The kwargs passed in from __init__

        Returns: None

        Raises:
            TaskMissingParametersException: If any of Task's parameters are in kwargs.
        """
        missing_parameters = []

        # Todo: Validate Arguments w/ Type Hints: Eventually we should do more then just validate an argument is present.

        for param in annotations.keys():
            try:
                setattr(self, param, kwargs[param])
            except KeyError:
                missing_parameters.append(param)

        if missing_parameters:
            raise TaskMissingParameterException(
                f"{self.__class__.__name__} requires the following parameters: {','.join(missing_parameters)}"
            )

        self._parameters = annotations.keys()


class Task(BaseTask):
    def __init__(
        self,
        *,
        params: Optional[TaskParams] = None,
        config: Optional[TaskConfig] = None,
        **kwargs,
    ):
        """
        A discrete unit of work to do.

        Args:
            config (TaskConfig): The configuration for the task. This is for runtime specific configuration.
            **kwargs: All the properties for a task should be passed here.
        """

        self._config = config
        self._completed = False
        self._stakeholders = set()
        self._set_parameters(kwargs, self._get_annotations())

    @classmethod
    def _get_annotations(cls):
        annotations = {}
        for c in cls.mro():
            try:
                annotations = annotations | c.__annotations__
            except AttributeError:
                pass

        return annotations

    def add_stakeholder(self, stakeholder_task: TaskType):

        self._stakeholders.add(stakeholder_task)

    ################################
    # Properties From here on down #
    # Please sort A to Z           #
    ################################

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, _):
        raise FrozenPropertyException(f"{self.task_name}.config cannot be modified.")

    @property
    def completed(self):
        return self.completed

    @completed.setter
    def completed(self, v: bool):

        if not isinstance(v, bool):
            raise ValueError(f"{self.task_name}.completed can only be a boolean value.")

        self._completed = v

    @property
    def id(self) -> str:
        """Returns"""
        return f"{self.__class__.__name__}_{'_'.join([str(getattr(self,p)) for p in self._parameters])}"

    @id.setter
    def id(self, _):
        raise FrozenPropertyException(f"{self.task_name}.id cannot be modified.")

    @property
    def ready(self) -> bool:
        if self.stakeholders:
            return all(stakeholder.completed for stakeholder in self.stakeholders)
        else:
            return True

    @ready.setter
    def ready(self, _):
        raise FrozenPropertyException(f"{self.task_name}.ready cannot be modified.")

    @property
    def requirements(self) -> Optional[List[TaskType]]:
        return None

    @property
    def stakeholders(self) -> Optional[Set[TaskType]]:
        return self._stakeholders

    @property
    def task_name(self) -> str:
        return self.__class__.__name__

    @task_name.setter
    def task_name(self, _):
        raise FrozenPropertyException(f"{self.task_name}.task_name cannot be modified.")


# TODO: Rename : This needs a better name then 'TaskList'
class TaskList:
    def __init__(self, initial_task: Task):

        self.tasks = {}

        self._build_task_list(initial_task)

    def _build_task_list(self, task: Task):

        self.tasks[task.id] = task

        if task.requirements:
            requirement_task: Task

            for requirement_task in task.requirements:
                if requirement_task.id in self.tasks.keys():
                    requirement_task = self.tasks[requirement_task.id]

                requirement_task.add_stakeholder(task)

                self.tasks[requirement_task.id] = requirement_task

                self._build_task_list(requirement_task)

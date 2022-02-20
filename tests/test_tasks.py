from morgo import Task


def test_task_set_parameters():
    class TaskWithParameters(Task):
        int_parameter: int

    task_instance = TaskWithParameters(int_parameter=1)
    assert task_instance.int_parameter == 1


def test_task_inherited_parameters():
    class ParentClass(Task):
        int_parameter: int

    class ChildClass(ParentClass):
        string_parameter: str

    task_instance = ChildClass(int_parameter=1, string_parameter="test")

    assert task_instance.int_parameter == 1
    assert task_instance.string_parameter == "test"


def test_task_with_mixed_inherited_parameters():
    class GrandParent(Task):
        int_parameter: int

    class ParentClass(GrandParent):
        pass

    class ChildClass(ParentClass):
        string_parameter: str

    task_instance = ChildClass(int_parameter=1, string_parameter="test")

    assert task_instance.int_parameter == 1
    assert task_instance.string_parameter == "test"

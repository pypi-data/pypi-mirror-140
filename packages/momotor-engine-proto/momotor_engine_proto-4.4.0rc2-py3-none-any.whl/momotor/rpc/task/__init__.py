import typing

from momotor.rpc.proto.task_pb2 import TaskId


def get_dotted_task_number(task_num: typing.Optional[typing.Sequence[int]]) -> typing.Optional[str]:
    """ Convert a task-number list into a dotted task-number.
    If task_num is empty or None, returns None

    >>> get_dotted_task_number(None)

    >>> get_dotted_task_number([])

    >>> get_dotted_task_number([0])
    '0'

    >>> get_dotted_task_number([0, 0])
    '0.0'

    :param task_num: The task number as a sequence
    :return: Dotted version of task number
    """
    return ".".join(str(t) for t in task_num) if task_num else None


def get_step_task_id(task_id: TaskId) -> str:
    """ Get the step task id from the :ref:`TaskId <momotor.rpc.proto.task>` message

    A step-task-id is the step-id followed with dot-separated sub task number(s)

    >>> get_step_task_id(TaskId(stepId='step'))
    'step'

    >>> get_step_task_id(TaskId(stepId='step', taskNumber=[0]))
    'step.0'

    >>> get_step_task_id(TaskId(stepId='step', taskNumber=[0, 0]))
    'step.0.0'

    :param task_id: The :ref:`TaskId <momotor.rpc.proto.task>` message
    :return: the step-task-id
    """
    step_id = task_id.stepId
    task_num = task_id.taskNumber
    return step_id + "." + get_dotted_task_number(task_num) if task_num else step_id

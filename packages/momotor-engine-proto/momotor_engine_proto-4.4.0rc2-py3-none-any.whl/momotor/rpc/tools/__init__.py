import dataclasses
import typing

from momotor.rpc.proto.tool_pb2 import Tool as ToolMessage

TN = typing.TypeVar('TN')


@dataclasses.dataclass(frozen=True)
class ProvidedTool(typing.Generic[TN]):
    #: name of the tool provided
    name: TN

    #: aliases that are provided by the same tool
    aliases: typing.Sequence[TN]


def tools_to_message(tools: typing.Iterable[ProvidedTool]) -> typing.Iterable[ToolMessage]:
    """ Convert an iterable of ProvidedTool objects into a sequence of Tool messages
    """
    for tool in tools:
        yield ToolMessage(
            name=str(tool.name),
            alias=(str(alias) for alias in tool.aliases)
        )


def message_to_tools(tool_message: typing.Optional[typing.Sequence[ToolMessage]]) -> typing.Iterable[ProvidedTool[str]]:
    """ Convert a sequence of Tool messages back into an iterable of ProvidedTool objects """
    if tool_message:
        for msg in tool_message:
            yield ProvidedTool(msg.name, tuple(msg.alias))

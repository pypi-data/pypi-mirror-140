from typing import Union
from pyconversation.loggers import BaseLogger
from pyconversation.util_types import MessageTransferGenerator
from .base import BaseMessage
from .transfer import MessageTransfer


class TerminateGroup(BaseMessage):
	child: Union[BaseMessage, None]

	def __init__(self, *, id: str, child: Union[BaseMessage, None] = None) -> None:
		super().__init__(id=id)
		self.child = child

	def _base_iterator(self, logger: BaseLogger) -> MessageTransferGenerator:
		if self.child:
			yield from self.child.iterator()

		yield MessageTransfer(id=self.id, skip=True, terminate_group=True)

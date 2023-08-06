from pyconversation.loggers import BaseLogger
from pyconversation.util_types import MessageTransferGenerator
from .base import BaseMessage
from .transfer import MessageTransfer


class Text(BaseMessage):
	text: str

	def __init__(self, *, id: str, text: str) -> None:
		super().__init__(id=id)
		self.text = text

	def _base_iterator(self, logger: BaseLogger) -> MessageTransferGenerator:
		yield MessageTransfer(id=self.id, text=self.text, skip=True)

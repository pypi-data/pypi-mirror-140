from pyconversation.loggers import BaseLogger
from pyconversation.util_types import MessageTransferGenerator
from .base import BaseMessage
from .transfer import MessageTransfer


class Ask(BaseMessage):
	text: str

	def __init__(self, *, id: str, text: str) -> None:
		super().__init__(id=id)
		self.text = text

	def _base_iterator(self, logger: BaseLogger) -> MessageTransferGenerator:
		answer = yield MessageTransfer(id=self.id, text=self.text)
		logger.log(self.id, answer)

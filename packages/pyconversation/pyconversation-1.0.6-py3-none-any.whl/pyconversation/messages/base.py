from pyconversation.loggers import BaseLogger
from pyconversation.util_types import MessageTransferGenerator

class BaseMessage:
	id: str

	def __init__(self, *, id: str) -> None:
		self.id = id

	def iterator(self, logger: BaseLogger) -> MessageTransferGenerator:
		logger.log_last_id(self.id)
		yield from self._base_iterator(logger)

	def _base_iterator(self, logger: BaseLogger) -> MessageTransferGenerator:
		raise NotImplementedError()

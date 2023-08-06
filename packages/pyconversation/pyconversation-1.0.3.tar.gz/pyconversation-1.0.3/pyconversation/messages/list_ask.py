from typing import Union
from pyconversation.loggers import BaseLogger
from pyconversation.util_types import MessageTransferGenerator
from .base import BaseMessage
from .transfer import MessageTransfer

class ListAsk(BaseMessage):
	text: str
	stop_command: str
	max_count: Union[int, None]

	def __init__(self, *, id: str, text: str, stop_command: str, max_count: Union[int, None]):
		super().__init__(id=id)
		self.text = text
		self.stop_command = stop_command.lower()
		self.max_count = max_count

	def _base_iterator(self, logger: BaseLogger) -> MessageTransferGenerator:
		yield MessageTransfer(id=self.id, text=self.text, skip=True)
		logger.set_array(self.id)
		
		count = 0
		answer = None

		while True:
			count += 1
			answer = yield MessageTransfer(id=f"{self.id}.{count}")

			if answer is None or answer.lower() == self.stop_command:
				break

			logger.add_array_item(self.id, answer)

			if self.max_count is not None and count >= self.max_count:
				break

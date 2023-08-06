from typing import Dict, Union
from pyconversation.loggers import BaseLogger
from pyconversation.util_types import MessageTransferGenerator
from .base import BaseMessage
from .transfer import MessageTransfer


class Switch(BaseMessage):
	text: str
	answer_map: Dict[str, BaseMessage]
	fallback: Union[BaseMessage, None]
	repeat_on_fallback: bool

	def __init__(
		self,
		*,
		id: str,
		text: str,
		answer_map: Dict[str, BaseMessage],
		fallback: Union[BaseMessage, None] = None,
		repeat_on_fallback: bool = False
	) -> None:
		super().__init__(id=id)
		self.text = text
		self.answer_map = answer_map
		self.fallback = fallback
		self.repeat_on_fallback = repeat_on_fallback

	def _base_iterator(self, logger: BaseLogger) -> MessageTransferGenerator:
		answer = yield MessageTransfer(id=self.id, text=self.text)
		from_map = self.answer_map.get(answer)
		logger.log(self.id, answer)

		if from_map:
			yield from from_map.iterator(logger)
		else:
			if self.fallback is not None:
				yield from self.fallback.iterator(logger)

			if self.repeat_on_fallback:
				yield from self.iterator(logger)

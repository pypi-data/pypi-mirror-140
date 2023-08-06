from typing import Callable, List, Dict, Union
from pyconversation.messages import BaseMessage, MessageTransfer
from pyconversation.loggers import BaseLogger
from pyconversation.util_types import MessageTransferGenerator

class MessageSender:
	logger: BaseLogger
	iterator: MessageTransferGenerator
	headline: Union[str, None]
	stop_command: Union[str, None]
	current_message: Union[MessageTransfer, None] = None
	resent_message: Union[MessageTransfer, None] = None
	base_send: Callable[[str], None]
	finished: bool = False
	terminated: bool = False

	def __init__(
		self,
		*,
		headline_text: Union[str, None] = None,
		stop_command: Union[str, None] = None,
		root: BaseMessage,
		logger: BaseLogger,
		send: Callable[[str], None]
	) -> None:
		self.logger = logger
		self.iterator = root.iterator(logger)
		self.base_send = send
		self.headline = headline_text
		self.stop_command = stop_command.lower() if stop_command is not None else None 

		self._send_headline()
		self._restore()

	def send_all_skippable(self, prev_answer: Union[str, None]) -> None:
		if prev_answer and prev_answer.lower() == self.stop_command:
			self.finished = True
			self.terminated = True

		if self.resent_message is not None:
			self._send(self.resent_message.text)
			self.resent_message = None

			if not self.current_message.skip:
				return

		while True:
			try:
				self.current_message = self.iterator.send(prev_answer)
				self._send(self.current_message.text)
			except StopIteration:
				self.finished = True
				break

			if not self.current_message.skip:
				break

	def finalize(self) -> Dict[str, Union[str, List[str]]]:
		self.iterator.close()

		result = self.logger.get_result_dict()
		self.logger.finalize()

		return result
	
	def _send(self, text: Union[str, None]) -> None:
		if text is not None:
			self.base_send(text)

	def _restore(self) -> None:
		last_id = self.logger.get_last_id()
		self.logger.reset_history()

		answer = None

		if last_id is not None:
			while True:
				try:
					self.current_message = self.iterator.send(answer)

					if self.current_message is None or self.current_message.id == last_id:
						break

					answer = self.logger.get(self.current_message.id)
				except StopIteration:
					self.finished = True
					break

		self.resent_message = self.current_message

	def _send_headline(self) -> None:
		self._send(self.headline)

from typing import Union


class MessageTransfer:
	id: str
	text: Union[str, None]
	skip: bool
	terminate_group: bool

	def __init__(
		self,
		*,
		id: str,
		text: Union[str, None] = None,
		skip: bool = False,
		terminate_group: bool = False
	) -> None:
		self.id = id
		self.text = text
		self.skip = skip
		self.terminate_group = terminate_group

from typing import Union, List, Dict
from .base import BaseLogger


class DictLogger(BaseLogger):
	result: Dict[str, Union[str, List[str]]] = {}
	history: List[str] = []

	def log(self, id: str, value: str) -> None:
		self.result[id] = value

	def set_array(self, id: str) -> None:
		self.result[id] = []

	def add_array_item(self, id: str, value: str) -> None:
		self.result[id].append(value)

	def get(self, id: str) -> Union[str, List[str], None]:
		return self.result.get(id)

	def get_result_dict(self) -> Dict[str, Union[str, List[str]]]:
		return self.result

	def reset_history(self) -> None:
		self.history.clear()

	def log_last_id(self, id: str) -> None:
		self.history.append(id)

	def get_last_id(self) -> Union[str, None]:
		count = len(self.history)

		if count == 0:
			return

		return self.history[count - 1]

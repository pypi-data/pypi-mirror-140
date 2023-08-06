from typing import Dict, List, Union


class BaseLogger:
	def log(self, id: str, value: str) -> None:
		raise NotImplementedError()

	def set_array(self, id: str) -> None:
		raise NotImplementedError()

	def add_array_item(self, id: str, value: str) -> None:
		raise NotImplementedError()

	def get(self, id: str) -> Union[str, List[str], None]:
		raise NotImplementedError()

	def get_result_dict(self) -> Dict[str, Union[str, List[str]]]:
		raise NotImplementedError()

	def reset_history(self) -> None:
		pass

	def log_last_id(self, id: str) -> None:
		pass

	def get_last_id(self) -> Union[str, None]:
		pass

	def toggle_readonly(self, is_readonly: bool) -> None:
		pass

	def finalize(self) -> None:
		pass

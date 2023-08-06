from typing import Union, List, Dict, Any
import os
import json
from io import TextIOWrapper
from .base import BaseLogger


class JsonFileLogger(BaseLogger):
	readonly: bool = False
	path: str
	file: TextIOWrapper
	cache: Dict[str, Any]

	def __init__(self, file_path: str) -> None:
		super().__init__()
		self.path = file_path
		
		open(file_path, "a").close()
		self.file = open(file_path, "r+")

		content = self.file.read()

		if content:
			self.cache = json.loads(content)
		else:
			self.cache = {"data": {}, "history": []}
			self._write()

	def log(self, id: str, value: str) -> None:
		if not self.readonly:
			self.cache["data"][id] = value
			self._write()

	def set_array(self, id: str) -> None:
		if not self.readonly:
			self.cache["data"][id] = []
			self._write()

	def add_array_item(self, id: str, value: str) -> None:
		if not self.readonly:
			self.cache["data"][id].append(value)
			self._write()

	def get(self, id: str) -> Union[str, List[str], None]:
		return self.cache["data"].get(id)

	def get_result_dict(self) -> Dict[str, Union[str, List[str]]]:
		return self.cache["data"]

	def reset_history(self) -> None:
		self.cache["history"] = []
		self._write()

	def log_last_id(self, id: str) -> None:
		self.cache["history"].append(id)
		self._write()

	def get_last_id(self) -> Union[str, None]:
		history = self.cache["history"]
		count = len(history)

		if count == 0:
			return
		
		return history[count - 1]

	def toggle_readonly(self, is_readonly: bool) -> None:
		self.readonly = is_readonly

	def finalize(self) -> None:
		self.file.close()
		os.remove(self.path)

	def _write(self) -> None:
		self.file.seek(0)
		self.file.write(json.dumps(self.cache))

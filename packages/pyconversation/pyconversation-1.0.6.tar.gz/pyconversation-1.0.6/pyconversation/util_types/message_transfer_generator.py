from typing import Generator, Union
from pyconversation.messages.transfer import MessageTransfer


MessageTransferGenerator = Generator[MessageTransfer, Union[str, None], None]

from aiohttp import ClientResponse
from . import Intruder
import abc

class StatusCodeIntruderSession(Intruder.IntruderSession[int],abc.ABC):
    async def _process_response(self, response: ClientResponse) -> int:
        return response.status
import asyncio
import aiohttp
import typing
import io
from urllib import parse
import logging
import pathlib

def parse_template(template: str):
    lines = template.split('\n')
    method, path = tuple(lines[0].split())[:2]
    i = 2
    while i < len(lines):
        line = lines[i]
        if line.strip() == '':
            break
        i += 1
    headers = '\r\n'.join(lines[2:i])
    i += 1
    body = ''.join(lines[i:])
    
    return method, path, headers, body

class IntruderSession():
    _host: str
    _base_method: str
    _base_path: str
    _base_headers: str
    _base_body: str
    _vars_to_filenames: typing.Dict[str,typing.Union[str,pathlib.Path]]
    _vars_to_files: typing.Dict[str,io.TextIOWrapper]
    _logger: logging.Logger
    _verify_ssl: bool

    def __init__(self, host: str, template: pathlib.Path, mapping: typing.Dict[str,pathlib.Path],verify_ssl:bool=True):
        with open(template) as f:
            self._host = host
            self._base_method, self._base_path, self._base_headers, self._base_body = parse_template(f.read())
        self._vars_to_filenames = dict(mapping)
        self._vars_to_files = {}
        self._logger = logging.getLogger("Intruder")
        self._verify_ssl = verify_ssl

        
    def __enter__(self)->"IntruderSession":
        for key in self._vars_to_filenames.keys():
            self._vars_to_files[key] = self._vars_to_filenames[key].open()
        return self

    def __exit__(self,exc_t,exc,exc_tb)->None:
        for file in self._vars_to_files.values():
            file.close()

    def _format_request_params(self,mp: typing.Dict[str,str])->typing.Tuple[str,str,typing.Dict[str,str],str]:
        method = self._base_method.format(**mp)
        path = self._base_path.format(**mp)
        raw_headers = self._base_headers.format(**mp)
        headers = {}
        for line in raw_headers.split('\n'):
            split_line = line.strip().split(': ',maxsplit=2) #TODO: support trailing whitespace
            if len(split_line) == 2:
                key, value = tuple(split_line)
            else:
                key = split_line[0]
                value = ''
            headers[key] = value
        body = self._base_body.format(**mp)

        return method, path, headers, body

    def _request_data_pitchfork(self):
        if len(self._vars_to_files.keys()) != len(self._vars_to_filenames):
            raise ValueError("Session was not entered (use the with keyword)")
        while True:
            empty_found = False
            values_map = {}
            for key in self._vars_to_files.keys():
                line = self._vars_to_files[key].readline()
                if line == '':
                    empty_found = True
                elif empty_found:
                    raise ValueError(f"file {self._vars_to_filenames[key]} was longer than the shortest file.")

                values_map[key] = parse.quote(line.strip()) #TODO: support trailing whitespace
            if empty_found:
                break
            yield self._format_request_params(values_map)

    async def _get_status_code(self, response: aiohttp.ClientResponse)->int:
        return response.status

    async def send_request(self,session: aiohttp.ClientSession, method: str, path: str, headers: typing.Dict[str,str], body: str, cb):
        async with session.__getattribute__(method.lower())(self._host + path,headers=headers,data=body,verify_ssl=self._verify_ssl) as response:
            output = await cb(response)
            self._logger.debug(f"{method} {path}: {output}")
            return output

    async def intrude_pitchfork(self, batch_size: int = 100, desired_value: typing.Optional[typing.Callable] = None):
        if desired_value is None:
            desired_value = self._get_status_code

        if batch_size <= 0:
            raise ValueError(f"batch size of {batch_size} is invaild; batches must be positive.")
        
        output = []
        param_iter = self._request_data_pitchfork()
        async with aiohttp.ClientSession() as session:
            while True:
                batch = []
                for _, params in zip(range(batch_size),param_iter):
                    batch.append(asyncio.create_task(self.send_request(session,*params,cb=desired_value)))
                if len(batch) == 0: #happens if param_iter is empty
                    break
                output.extend(await asyncio.gather(*batch))
        return output
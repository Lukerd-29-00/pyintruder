from . import Intruder
import abc
import typing
from urllib import parse
T = typing.TypeVar("T")
c = abc.ABC()
class PitchforkInruderSession(typing.Generic[T],Intruder.IntruderSession[T],abc.ABC):
    def _request_data(self) -> typing.Generator[typing.Tuple[str,str,typing.Dict[str,str],str],None,None]:
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
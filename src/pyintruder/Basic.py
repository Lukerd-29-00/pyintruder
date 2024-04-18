from . import PitchforkIntruder
from . import StatusCodeIntruder

class StatusCodePitchforkIntruderSession(StatusCodeIntruder.StatusCodeIntruderSession,PitchforkIntruder.PitchforkInruderSession[int]):
    pass

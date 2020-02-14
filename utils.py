from functools import wraps
from .command import *


def active_mode(func):
    @wraps(func)
    def decorated(self, *args, **kwargs):
        if self.communication_mode == CommandValue.Passive and args:
            self.set_communication_mode(CommandValue.Active)
        return func(self, *args, **kwargs)
    return decorated


def passive_mode(func):
    @wraps(func)
    def decorated(self, *args, **kwargs):
        if self.communication_mode == CommandValue.Active:
            self.set_communication_mode(CommandValue.Passive)
        return func(self, *args, **kwargs)
    return decorated

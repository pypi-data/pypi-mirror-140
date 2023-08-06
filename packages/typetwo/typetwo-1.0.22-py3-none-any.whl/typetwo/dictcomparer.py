from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Callable

class DictComparer():
    """Compares 2 dictionaries, ignoring the specified keys"""    
    
    def __init__(
        self, 
        *ignore_fields
    ):
        self.ignore_fields = ignore_fields
   
    def __call__(self, a, b):
        """Compares 2 dictionaries, ignoring the specified keys"""
        if isinstance(a, dict) and isinstance(b, dict):
            a = {k:v for k,v in a.items() if k not in self.ignore_fields}
            b = {k:v for k,v in b.items() if k not in self.ignore_fields}
        return a == b

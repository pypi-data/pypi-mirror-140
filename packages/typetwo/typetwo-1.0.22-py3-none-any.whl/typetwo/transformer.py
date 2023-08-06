from datetime import date, datetime, time
from typing import Any, Callable

class Transformer():
    """
    A Transformer encapsulates a succession of
    functions which attempt to convert a value
    from one form to another.

    When called, the transformer applies each
    function in series, returning the value  
    from the first function to succesfully produce
    a new (different) value.

    ``in_place`` causes the transform to mutate values in 
    dicts and arrays when True. Otherwise, copies are 
    made and the original dict / array if left unchanged.

    Errors raised by transforms are ignored.
    """    
    def __init__(
        self, 
        *transforms
    ):
        self.transforms = list(transforms) if transforms else []


    def __add__(self, value : Callable[[Any], Any]):
        """Adds a transform function to this transformer.
        
        The transformer must be a simple function,
        taking a single value and returning a single value.
        
        Any errors raised by the transform function are ignored.
        """
        if isinstance(value, Transformer):
            return Transformer(*self.transforms, *value.transforms)
        if isinstance(value, function):            
            return Transformer(*self.transforms, value)
        else:
            raise NotImplementedError()

    def __call__(self, value, in_place : bool = True):
        """Applies this transform to the given ``value``. 
        Returns the original value if no transform succeeds"""

        if value is not None:  
            if isinstance(value, list):
                if in_place:
                    for i, d in enumerate(value):
                        value[i] = self(d, in_place = in_place) 
                    return value
                else:
                    return [self(d, in_place = in_place) for d in value]

            if isinstance(value, dict):
                if in_place:
                    for i, d in value.items():
                        value[i] = self(d, in_place = in_place) 
                    return value
                else:
                    return {key: self(v, in_place = in_place) for (key, v) in value.items()}
            
            for fn_xform in self.transforms:
                try:
                    new_value = fn_xform(value)
                    if new_value is not None and new_value != value:
                        return new_value
                except Exception as e:
                    pass
        return value
      
    def enable_dates(self, *formats):
        """Adds date format strings to recognize (see strptime)"""
        def make_formatter(format):
            return lambda d: datetime.strptime(d, format).date()
        self.transforms += [make_formatter(f) for f in formats]
        return self
    
    def enable_times(self, *formats):
        """Adds time format strings to recognize (see strptime)"""
        def make_formatter(format):
            return lambda d: datetime.strptime(d, format).time()
        self.transforms += [make_formatter(f) for f in formats]
        return self
    
    def enable_datetimes(self, *formats):
        """Adds datetime format strings to recognize (see strptime)"""
        def make_formatter(format):
            return lambda d: datetime.strptime(d, format)
        self.transforms += [make_formatter(f) for f in formats]
        return self

    def enable_iso_dates(self):
        """Adds support for parsing ISO date, time and datetime strings"""
        self.transforms += [time.fromisoformat, date.fromisoformat, datetime.fromisoformat]
        return self        



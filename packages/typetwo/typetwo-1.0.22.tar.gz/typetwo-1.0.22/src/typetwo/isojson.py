import json
from datetime import date, datetime, time
from typing import Iterable

from .transformer import Transformer


class IsoJson(json.JSONEncoder):
    '''
    Encodes a dict to JSON with date, time and datetime expressed in ISO format.
    '''
    def _preprocess(self, obj):
        if isinstance(obj, (date, datetime, time)):
            return obj.isoformat()
        if isinstance(obj, dict):
            return {self._preprocess(k): self._preprocess(v) for k,v in obj.items()}
        if isinstance(obj, list):
            return [self._preprocess(i) for i in obj]
        return obj

    def default(self, obj):
        if isinstance(obj, (date, datetime, time)):
            return obj.isoformat()
        return super().default(obj)

    def iterencode(self, obj, _one_shot=False):
        return super().iterencode(self._preprocess(obj), _one_shot=_one_shot)
    
    @classmethod
    def dumps(cls, data):
        '''
        Returns a JSON string representation of data, 
        with conversion of date, time and datetime to 
        ISO format strings.
        '''        
        return cls().encode(data)

    @classmethod
    def dump_jsonl(cls, data):
        '''
        Returns a JSON-lines format representation of
        the list or data passed.
        '''
        instance = cls()

        if isinstance(data, Iterable):
            return '\n'.join((instance.dumps(item) for item in data))
        return instance.encode(data)


    """
    Attempts to parse any ISO date, time or datetime values to their native python types
    """
    parse_iso_dates = Transformer(time.fromisoformat, date.fromisoformat, datetime.fromisoformat)

    """
    Attempts to parse any date, time or datetime values to their native python types
    """
    parse_extra_dates = Transformer()\
        .enable_dates("%Y-%m-%d","%d/%m/%Y","%d-%b-%Y","%d-%m-%Y")\
        .enable_iso_dates()


    @classmethod
    def loads(cls, json_text : str, hook = None) -> dict:
        """
        Loads json data, with conversion of 
        ISO date, time and datetime to
        their respective Python types.
        """
        hook = hook or cls.parse_iso_dates
        return json.loads(json_text, object_hook=hook)


    @classmethod
    def load_lines(cls, json_text : str, hook = None) -> list:
        """
        Parses JSON-lines data and 
        returns a list of dicts, with 
        data parsed to native types using
        the given parser functions
        """
        hook = hook or cls.parse_iso_dates
        return [
            json.loads(txt, object_hook=hook) 
            for txt in json_text.splitlines()
            ] if json_text else []

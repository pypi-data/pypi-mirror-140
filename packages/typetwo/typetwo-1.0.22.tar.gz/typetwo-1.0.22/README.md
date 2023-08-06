# Type Two

Provides a simple set of classes for handling type-II slowly changing dimension style data.
Also provides helper classes for reading and writing JSON payloads with ISO-compliant dates.

## Example Usage: TypeTwo

 ```python
rows = [
    {"id": 1, "name": "Henry", "age": 34}
    {"id": 2, "name": "Fred", "age" : 42}
]

history = TypeType(rows, RowKey("id"), from_field = "start", to_field = "end")
iter(history)
>>> {"id": 1, "name": "Henry", "age": 34, "start": datetime(1900,1,1),  "end": datetime(2999,12,31)}
>>> {"id": 2, "name": "Fred",  "age": 42, "start": datetime(1900,1,1),  "end": datetime(2999,12,31)}


history += {"id": 1, "name": "Henry", "age": 37}
iter(history)
>>> {"id": 1, "name": "Henry", "age": 34, "start": datetime(1900,1,1),  "end": datetime(2022,6,12,3,0,0)}
>>> {"id": 1, "name": "Henry", "age": 37, "start": datetime(2022,6,12,3,0,0), "end": datetime(2999,12,31)}
>>> {"id": 2, "name": "Fred",  "age": 42, "start": datetime(1900,1,1),  "end": datetime(2999,12,31)}

history += [
    {"id": 1, "name": "Henry", "age": 99}
    {"id": 2, "name": "Fred", "age": 99}
]

iter(history)
>>> {"id": 1, "name": "Henry", "age": 34, "start": datetime(1900,1,1),        "end": datetime(2022,6,12,3,0,0)}
>>> {"id": 1, "name": "Henry", "age": 37, "start": datetime(2022,6,12,3,0,0), "end": datetimedatetime(2022,6,12,3,15,0)}
>>> {"id": 1, "name": "Henry", "age": 99, "start": datetime(2022,6,12,3,15,0),"end": datetime(2999,12,31)}
>>> {"id": 2, "name": "Fred",  "age": 42, "start": datetime(1900,1,1),        "end": datetime(2022,6,12,3,15,0)}
>>> {"id": 2, "name": "Fred",  "age": 99, "start": datetime(2022,6,12,3,15,0),"end": datetime(2999,12,31)}
```
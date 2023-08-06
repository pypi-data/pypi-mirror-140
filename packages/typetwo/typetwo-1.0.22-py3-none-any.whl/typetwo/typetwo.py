from datetime import date, datetime
import types
from typing import Any, AnyStr, Callable, Dict, List, Tuple, Union

from .dictcomparer import DictComparer
from .rowkey import RowKey, FunKey, NoKey


class TypeTwo():
    """
    Performs Type-II slowly changed dimension data processing on a list of dicts
    """

    def __init__(self, 
        row_key     : Union[RowKey, str, List[str]],
        existing_rows : List[Dict[str, Any]] = [],
        from_field  : str  = '__FROM__', 
        to_field    : str  = '__TO__', 
        curr_field  : str   = '__CURRENT__', 
        from_date   : datetime = datetime.min,
        to_date     : datetime = datetime(2999,12,31), 
        fn_can_retire : Callable[[dict], bool] = lambda _ : True,
        ignore_fields = []
    ):
        """
        Initializes an object which maintains state of a 
        set of rows upon which type-II slowly changed 
        dimension data processing is performed.

        existing_rows is a list of previously processed rows.
        row_key describes the primary key for records.

        from_field, to_field and current_key [all optional] are
        the names to be used for record validity fields. 
        i.e. fields to specify when a record became valid, 
        when it ceased to be valid, and whether it is 
        presently deemed valid.

        from_date and to_date are the default values to 
        assign to the record validity ranges.    
                
        fn_can_retire helps determine whether a record may be 
        retired, and defaults to always returning True. This 
        allows the caller to prevent the retirement of records
        that haven't appeared in the current source list.

        ignore_fields allows additional fields to be ignored
        when comparing rows for changes. This is useful when 
        extract timestamp values appear in source data.
        
        time_now defines the timestamp used for switching validity
        of any newly added record.
        """
        if isinstance(row_key, str):
            row_key = RowKey(row_key)
        elif isinstance(row_key, list):
            row_key = RowKey(*row_key)
        elif row_key is None:
            row_key = NoKey()
        elif isinstance(row_key, types.FunctionType):
            row_key = FunKey(row_key)
        elif isinstance(row_key, RowKey):
            self.row_key = row_key
        else:
            raise NotImplementedError()

        self.from_field = from_field
        self.to_field = to_field
        self.current_key = curr_field
        self.from_date = from_date
        self.to_date = to_date 
        self.fn_can_retire = fn_can_retire 
        self.comparer = DictComparer(from_field, to_field, curr_field, *ignore_fields)
        self.visited_keys = set([])
        self.has_changes = False

        for row in existing_rows:
            row.setdefault(from_field, from_date)
            row.setdefault(to_field, to_date)
            row.setdefault(curr_field, True)
  
        self.document = row_key.group_rows(existing_rows)
        
        for rows in self.document.values():
            if len(rows) > 1:                
                rows.sort(key = lambda r : r[from_field], reverse = True)
                for i, row in enumerate(rows):
                    if i > 0:
                        row[curr_field] = False

    def process_row(self, row, time_now = datetime.now()):
        """
        Args:
            row: dict   A now-current row from a system of record.
            self.time_now:   The timestamp to use for the change of record validity            

        Returns:
            True if the row was new or changed, else False if it had no effect on existing data.
        """
        
        if not isinstance(row, dict):
            raise NotImplementedError

        key = self.row_key(row)
        self.visited_keys.add(key)
        section = self.document.setdefault(key, [])
        existing = [e for e in section if e[self.current_key]]
        if existing:
            existing = existing[0]

            if self.comparer(row, existing):
                return False

            row.setdefault(self.from_field, time_now)
            existing[self.to_field] = row[self.from_field]
            existing[self.current_key] = False
        else:
            row.setdefault(self.from_field, self.from_date)

        row.setdefault(self.to_field, self.to_date)
        row.setdefault(self.current_key, True)        
        section.insert(0, row)
        self.has_changes = True
        return True


    def process_rows(self, current_rows : list):
        """
        Args:
            rows: list   The now-current rows from a system of record.
            
        Returns:
            A list of processed rows, sorted by section in descending order of change (i.e. newest first)
        """
        for row in current_rows:
            self.process_row(row)

        return iter(self)

    def __add__(self, other):
        """Add either a new row, or a list of new rows to the existing data"""
        if isinstance(other, list):
            self.process_rows(other)
        elif isinstance(other, dict):
            self.process_row(other)
        else:
            return NotImplemented
        return self            

    def __iter__(self):
        """Iterates over the SCD-II processed rows"""        
        time_now = datetime.now()

        for key, section in self.document.items():
            for i, row in enumerate(section):
                if i == 0:
                    if row[self.current_key] and (key not in self.visited_keys):
                        if self.fn_can_retire(row):
                            row[self.current_key] = False
                            row[self.to_field] = time_now
                            self.has_changes = True
                else:
                    row[self.current_key] = False
                    to_date = section[i-1][self.from_field] 
                    if row[self.to_field] is None or row[self.to_field] > to_date:
                        row[self.to_field] = to_date
                        self.has_changes = True
                yield row

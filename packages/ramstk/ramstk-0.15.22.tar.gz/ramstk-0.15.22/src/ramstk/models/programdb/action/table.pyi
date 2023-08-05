# Standard Library Imports
from typing import Any, Dict

# RAMSTK Package Imports
from ramstk.models import RAMSTKActionRecord as RAMSTKActionRecord
from ramstk.models import RAMSTKBaseTable as RAMSTKBaseTable

class RAMSTKActionTable(RAMSTKBaseTable):
    _db_id_colname: str = ...
    _db_tablename: str = ...
    _select_msg: str = ...
    _tag: str = ...
    _lst_id_columns: Any = ...
    _record: Any = ...
    pkey: str = ...
    def __init__(self, **kwargs: Dict[str, Any]) -> None: ...
    def do_get_new_record(self, attributes: Dict[str, Any]) -> object: ...

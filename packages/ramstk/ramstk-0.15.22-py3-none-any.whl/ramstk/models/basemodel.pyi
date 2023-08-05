# Standard Library Imports
from typing import Any, Dict, List

# Third Party Imports
import treelib

# RAMSTK Package Imports
from ramstk.db.base import BaseDatabase as BaseDatabase
from ramstk.exceptions import DataAccessError as DataAccessError
from ramstk.utilities import none_to_default as none_to_default

def do_clear_tree(tree: treelib.Tree) -> treelib.Tree: ...

class RAMSTKBaseRecord:
    def set_attributes(self, attributes) -> None: ...

class RAMSTKBaseTable:
    _db_id_colname: str
    _db_tablename: str
    _root: int
    _select_msg: str
    _tag: str
    _fkey: Any
    _pkey: Any
    _lst_id_columns: Any
    _parent_id: int
    _record: Any
    _revision_id: int
    dao: Any
    last_id: int
    pkey: str
    tree: Any
    do_get_new_record: Any
    def __init__(self, **kwargs: Dict[str, Any]) -> None: ...
    def do_connect(self, dao: BaseDatabase) -> None: ...
    def do_create_all_codes(self, prefix: str) -> None: ...
    def do_delete(self, node_id: int) -> None: ...
    def do_get_attributes(self, node_id: int, table: str = ...) -> None: ...
    def do_get_tree(self) -> None: ...
    def do_insert(self, attributes: Dict[str, Any]) -> None: ...
    def do_select(self, node_id: Any) -> Any: ...
    def do_select_all(self, attributes: Dict[str, Any]) -> None: ...
    def do_set_attributes(self, node_id: List, package: Dict[str, Any]) -> None: ...
    def do_set_attributes_all(self, attributes: Dict[str, Any]) -> None: ...
    def do_set_tree(self, tree: treelib.Tree) -> None: ...
    def do_update(self, node_id: int, table: str = ...) -> None: ...
    def do_update_all(self) -> None: ...

class RAMSTKBaseView:
    _root: int
    _tag: str
    _dic_load_functions: Any
    _dic_trees: Any
    _lst_modules: Any
    _revision_id: int
    dao: Any
    tree: Any
    def __init__(self, **kwargs: Dict[str, Any]) -> None: ...
    def do_set_tree(self, tree: treelib.Tree) -> None: ...
    def on_select_all(self) -> None: ...

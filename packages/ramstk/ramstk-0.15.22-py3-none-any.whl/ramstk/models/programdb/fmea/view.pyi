# Standard Library Imports
from typing import Any, Dict

# RAMSTK Package Imports
from ramstk.models import RAMSTKBaseView as RAMSTKBaseView

class RAMSTKFMEAView(RAMSTKBaseView):
    _root: int = ...
    _tag: str = ...
    _dic_load_functions: Any = ...
    _dic_trees: Any = ...
    _lst_modules: Any = ...
    def __init__(self, **kwargs: Dict[Any, Any]) -> None: ...
    def _do_load_modes(self) -> None: ...
    def _do_load_mechanisms(self, mode_id: int) -> None: ...
    def _do_load_causes(self, mechanism_id: int, parent_id: str) -> None: ...
    def _do_load_controls(self, cause_id: int, parent_id: str) -> None: ...
    def _do_load_actions(self, cause_id: int, parent_id: str) -> None: ...

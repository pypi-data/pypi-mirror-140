# Standard Library Imports
from typing import Any, Dict, List

# RAMSTK Package Imports
from ramstk.views.gtk3.milhdbk217f import MilHdbk217FResultPanel
from ramstk.views.gtk3.widgets import RAMSTKEntry

class ICMilHdbk217FResultPanel(MilHdbk217FResultPanel):
    _dic_part_stress: Dict[int, str]
    _title: str
    txtC1: RAMSTKEntry
    txtC2: RAMSTKEntry
    txtLambdaBD: RAMSTKEntry
    txtLambdaBP: RAMSTKEntry
    txtLambdaCYC: RAMSTKEntry
    txtLambdaEOS: RAMSTKEntry
    txtPiA: RAMSTKEntry
    txtPiCD: RAMSTKEntry
    txtPiL: RAMSTKEntry
    txtPiMFG: RAMSTKEntry
    txtPiPT: RAMSTKEntry
    txtPiT: RAMSTKEntry
    dic_attribute_widget_map: Dict[str, List[Any]]
    def __init__(self) -> None: ...
    def _do_load_entries(self, attributes: Dict[str, Any]) -> None: ...

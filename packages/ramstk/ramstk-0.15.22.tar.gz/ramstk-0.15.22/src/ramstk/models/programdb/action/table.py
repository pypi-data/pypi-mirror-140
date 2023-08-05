# -*- coding: utf-8 -*-
#
#       ramstk.models.action.table.py is part of The RAMSTK Project
#
# All rights reserved.
# Copyright since 2007 Doyle "weibullguy" Rowland doyle.rowland <AT> reliaqual <DOT> com
"""FMEA Action Package Data Controller."""

# Standard Library Imports
from typing import Any, Dict, Type

# RAMSTK Package Imports
from ramstk.models import RAMSTKActionRecord, RAMSTKBaseTable


class RAMSTKActionTable(RAMSTKBaseTable):
    """Contain the attributes and methods of the FMEA Action data manager."""

    # Define private dictionary class attributes.

    # Define private list class attributes.

    # Define private scalar class attributes.
    _db_id_colname = "fld_action_id"
    _db_tablename = "ramstk_action"
    _deprecated = False
    _select_msg = "selected_revision"
    _tag = "action"

    # Define public dictionary class attributes.

    # Define public list class attributes.

    # Define public scalar class attributes.

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """Initialize a FMEA Action data manager instance."""
        super().__init__(**kwargs)

        # Initialize private dictionary attributes.

        # Initialize private list attributes.
        self._lst_id_columns = [
            "revision_id",
            "hardware_id",
            "mode_id",
            "mechanism_id",
            "cause_id",
            "action_id",
        ]

        # Initialize private scalar attributes.
        self._record: Type[RAMSTKActionRecord] = RAMSTKActionRecord

        # Initialize public dictionary attributes.

        # Initialize public list attributes.

        # Initialize public scalar attributes.
        self.pkey = "action_id"

        # Subscribe to PyPubSub messages.

    def do_get_new_record(  # pylint: disable=method-hidden
        self, attributes: Dict[str, Any]
    ) -> object:
        """Gets a new record instance with attributes set.

        :param attributes: the dict of attribute values to assign to the new record.
        :return: None
        :rtype: None
        """
        _new_record = self._record()
        _new_record.revision_id = attributes["revision_id"]
        _new_record.hardware_id = attributes["hardware_id"]
        _new_record.mode_id = attributes["mode_id"]
        _new_record.mechanism_id = attributes["mechanism_id"]
        _new_record.cause_id = attributes["cause_id"]
        _new_record.action_id = self.last_id + 1

        return _new_record

# -*- coding: utf-8 -*-
#
#       ramstk.models.commondb.failure_mode.record.py is part of The RAMSTK Project
#
# All rights reserved.
# Copyright since 2007 Doyle "weibullguy" Rowland doyle.rowland <AT> reliaqual <DOT> com
"""Failure Mode Record Model."""

# Third Party Imports
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

# RAMSTK Package Imports
from ramstk.db import RAMSTK_BASE
from ramstk.models import RAMSTKBaseRecord


class RAMSTKFailureModeRecord(RAMSTK_BASE, RAMSTKBaseRecord):
    """Class to represent ramstk_failuremode in the RAMSTK Common database."""

    __defaults__ = {
        "description": "Failure Mode Description",
        "mode_ratio": 1.0,
        "source": "",
    }
    __tablename__ = "ramstk_failure_mode"
    __table_args__ = {"extend_existing": True}

    category_id = Column(
        "fld_category_id",
        Integer,
        ForeignKey("ramstk_category.fld_category_id"),
        nullable=False,
    )
    subcategory_id = Column(
        "fld_subcategory_id",
        Integer,
        ForeignKey("ramstk_subcategory.fld_subcategory_id"),
        nullable=False,
    )
    mode_id = Column(
        "fld_failuremode_id",
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    description = Column(
        "fld_description",
        String(512),
        default=__defaults__["description"],
    )
    mode_ratio = Column("fld_mode_ratio", Float, default=__defaults__["mode_ratio"])
    source = Column("fld_source", String(128), default=__defaults__["source"])

    # Define the relationships to other tables in the RAMSTK Program database.
    category = relationship(  # type: ignore
        "RAMSTKCategoryRecord",
        back_populates="mode",
    )
    subcategory = relationship(  # type: ignore
        "RAMSTKSubCategoryRecord", back_populates="mode"
    )

    def get_attributes(self):
        """Retrieve current values of RAMSTKFailureMode data model attributes.

        :return: {failuremode_id, description, type} pairs
        :rtype: dict
        """
        return {
            "category_id": self.category_id,
            "subcategory_id": self.subcategory_id,
            "mode_id": self.mode_id,
            "description": self.description,
            "mode_ratio": self.mode_ratio,
            "source": self.source,
        }

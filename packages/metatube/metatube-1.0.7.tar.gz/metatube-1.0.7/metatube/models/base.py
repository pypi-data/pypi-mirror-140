#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright (C) 2019 Christoph Fink, University of Helsinki
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 3
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, see <http://www.gnu.org/licenses/>.

"""A common sqlalchemy declarative_base() to share between models."""


__all__ = ["Base"]


import hashlib
import re

import sqlalchemy.ext.declarative
import sqlalchemy.orm

from ..config import Config


CAMEL_CASE_TO_SNAKE_CASE_RE = re.compile(
    "((?<=[a-z0-9])[A-Z]|(?!^)(?<!_)[A-Z](?=[a-z]))"
)


def camel_case_to_snake_case(camel_case):
    """Convert a `camelCase` string to `snake_case`."""
    snake_case = CAMEL_CASE_TO_SNAKE_CASE_RE.sub(r"_\1", camel_case).lower()
    return snake_case


class Base:
    """Wrapper around sqlalchemy declarative_base() to add shared functionality."""

    @staticmethod
    def integer_hash(data):
        """Returns a BLAKE2 hash of data, in integer representation."""
        return int.from_bytes(
            hashlib.blake2b(data.encode("UTF-8"), digest_size=7).digest(),
            "big"
        )

    @staticmethod
    def pseudonymise_identifiers():
        pseudonymise_identifiers = True
        try:
            with Config() as config:
                if config["pseudonymise"] is False:
                    pseudonymise_identifiers = False
        except KeyError:
            pass
        return pseudonymise_identifiers

    @sqlalchemy.orm.declared_attr
    def __tablename__(cls):
        snake_case = camel_case_to_snake_case(cls.__name__)
        return "{:s}s".format(snake_case)


Base = sqlalchemy.ext.declarative.declarative_base(cls=Base)

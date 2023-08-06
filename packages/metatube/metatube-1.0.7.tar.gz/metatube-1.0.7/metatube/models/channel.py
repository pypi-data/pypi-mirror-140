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

"""A YouTube channel ORM data model."""


__all__ = ["Channel"]


import dataclasses

import sqlalchemy

from .base import Base


@dataclasses.dataclass
class Channel(Base):
    """A YouTube channel ORM data model."""

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)

    title = sqlalchemy.Column(sqlalchemy.Text)

    channel_id = sqlalchemy.Column(sqlalchemy.Text)
    channel_url = sqlalchemy.Column(
        sqlalchemy.Text,
        sqlalchemy.Computed("'http://www.youtube.com/channel/' || channel_id || '/'"),
    )

    videos = sqlalchemy.orm.relationship("Video", back_populates="channel")

    # might be a user’s “personal” channel
    user = sqlalchemy.orm.relationship("User", uselist=False, back_populates="channel")

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

"""A YouTube user ORM data model."""


__all__ = ["User"]


import dataclasses

import sqlalchemy

from .base import Base
from .channel import Channel


#  # EXAMPLE record
#  {
#   "authorDisplayName": "Sugyono Saja",
#   "authorProfileImageUrl": "https://yt3.ggpht.com/a/AGF-l7_eYs...j-mo",
#   "authorChannelUrl": "http://www.youtube.com/channel/UCVMHlmXv...",
#   "authorChannelId": {
#    "value": "UCVMHlmXvrgh-SASkqFy5nPw"
#   },


@dataclasses.dataclass
class User(Base):
    """A YouTube user ORM data model."""

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)

    name = sqlalchemy.Column(sqlalchemy.Text)

    channel_id = sqlalchemy.Column(
        sqlalchemy.BigInteger, sqlalchemy.ForeignKey("channels.id")
    )
    channel = sqlalchemy.orm.relationship("Channel", back_populates="user")

    comments = sqlalchemy.orm.relationship("Comment", back_populates="user")
    videos = sqlalchemy.orm.relationship("Video", back_populates="user")

    @classmethod
    def from_raw_api_json(cls, data):
        """
        Create a user model from raw API data.

        Initialise a new User() using a (JSON) dict as returned from the
        YouTube Data API (see EXAMPLE record above).

        This currently only works with data as returned by
        the https://www.googleapis.com/youtube/v3/commentThreads endpoint
        """
        _data = {}
        _channel_data = {}

        _id = cls.integer_hash(data["authorChannelId"]["value"])

        _data["id"] = _id
        _channel_data["id"] = _id

        if not cls.pseudonymise_identifiers():
            _data["name"] = data["authorDisplayName"]
            _channel_data["channel_id"] = data["authorChannelId"]["value"]
            _channel_data["title"] = data["authorDisplayName"]

        _data["channel"] = Channel(**_channel_data)

        return cls(**_data)

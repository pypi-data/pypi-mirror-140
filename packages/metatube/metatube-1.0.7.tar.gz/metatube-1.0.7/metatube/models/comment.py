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

"""A YouTube comment ORM data model."""


__all__ = ["Comment"]


import dataclasses

import dateparser
import sqlalchemy

from .base import Base
from .user import User


#  # EXAMPLE record
#  {
#   "kind": "youtube#comment",
#   "etag": "\"SJZWTG6xR0eGuCOh2bX6w3s4F94/EwwgqCUTedRz4UQ0YrMDealtuec\"",
#   "id": "Ugw1hpNW--cMCwhG-wJ4AaABAg.90k0KongL2A90sDm4BCnYb",
#   "snippet": {
#    "authorDisplayName": "Sugyono Saja",
#    "authorProfileImageUrl": "https://yt3.ggpht.com/a/AGF-l7_eYs...j-mo",
#    "authorChannelUrl": "http://www.youtube.com/channel/UCVMHlmXv...",
#    "authorChannelId": {
#     "value": "UCVMHlmXvrgh-SASkqFy5nPw"
#    },
#    "videoId": "wJitjtID0cc",
#    "textDisplay": "Bikin burung laen drop. Suara kasar dan kerras",
#    "textOriginal": "Bikin burung laen drop. Suara kasar dan kerras",
#    "parentId": "Ugw1hpNW--cMCwhG-wJ4AaABAg",
#    "canRate": true,
#    "viewerRating": "none",
#    "likeCount": 1,
#    "publishedAt": "2019-11-03T11:36:28.000Z",
#    "updatedAt": "2019-11-03T11:36:28.000Z"
#   }
# }


@dataclasses.dataclass
class Comment(Base):
    """A YouTube comment ORM data model."""

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)

    user_id = sqlalchemy.Column(
        sqlalchemy.BigInteger, sqlalchemy.ForeignKey("users.id")
    )
    user = sqlalchemy.orm.relationship("User", back_populates="comments")

    comment_thread_id = sqlalchemy.Column(
        sqlalchemy.BigInteger, sqlalchemy.ForeignKey("comment_threads.id")
    )
    comment_thread = sqlalchemy.orm.relationship(
        "CommentThread", back_populates="comments"
    )
    order_in_comment_thread = sqlalchemy.Column(sqlalchemy.Integer)

    published = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True))
    updated = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True))

    text = sqlalchemy.Column(sqlalchemy.Text)

    @classmethod
    def from_raw_api_json(cls, data, order_in_comment_thread=None):
        """
        Create a video model from raw API data.

        Initialise a new Video() using a (JSON) dict as returned from the
        YouTube Data API (see EXAMPLE record above).
        """
        _data = {}

        _data["id"] = cls.integer_hash(data["id"])

        _data["user"] = User.from_raw_api_json(data["snippet"])

        if order_in_comment_thread is not None:
            _data["order_in_comment_thread"] = order_in_comment_thread

        _data["published"] = dateparser.parse(data["snippet"]["publishedAt"])
        _data["updated"] = dateparser.parse(data["snippet"]["updatedAt"])

        _data["text"] = data["snippet"]["textOriginal"]

        return cls(**_data)

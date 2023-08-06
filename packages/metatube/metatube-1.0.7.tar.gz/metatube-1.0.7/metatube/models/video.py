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

"""A YouTube video ORM data model."""


__all__ = ["Video"]

import dataclasses

import dateparser
import sqlalchemy

from .base import Base
from .channel import Channel
from .user import User


#  # EXAMPLE record
#  {
#   "kind": "youtube#searchResult",
#   "etag": "\"SJZWTG6xR0eGuCOh2bX6w3s4F94/XUIrQ-4pn8OEdWxKzr87gUo0L3U\"",
#   "id": {
#    "kind": "youtube#video",
#    "videoId": "dGqZg2eeFPw"
#   },
#   "snippet": {
#    "publishedAt": "2018-12-26T08:56:17.000Z",
#    "channelId": "UC3YsVCnrtanUqE02uE7Akyw",
#    "title": "Masteran Poksai mandarin,Ngeplong vol keras",
#    "description": "Masteran poksai mandarin langsung nyaut.",
#    "thumbnails": {
#     "default": {
#      "url": "https://i.ytimg.com/vi/dGqZg2eeFPw/default.jpg",
#      "width": 120,
#      "height": 90
#     },
#     "medium": {
#      "url": "https://i.ytimg.com/vi/dGqZg2eeFPw/mqdefault.jpg",
#      "width": 320,
#      "height": 180
#     },
#     "high": {
#      "url": "https://i.ytimg.com/vi/dGqZg2eeFPw/hqdefault.jpg",
#      "width": 480,
#      "height": 360
#     }
#    },
#    "channelTitle": "KICAU NUSANTARA",
#    "liveBroadcastContent": "none"
#   }
#  }


@dataclasses.dataclass
class Video(Base):
    """A YouTube video ORM data model."""

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)

    video_id = sqlalchemy.Column(sqlalchemy.Text)

    title = sqlalchemy.Column(sqlalchemy.Text)
    description = sqlalchemy.Column(sqlalchemy.Text)
    published = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True))

    channel_id = sqlalchemy.Column(
        sqlalchemy.BigInteger, sqlalchemy.ForeignKey("channels.id")
    )
    channel = sqlalchemy.orm.relationship("Channel", back_populates="videos")

    user_id = sqlalchemy.Column(
        sqlalchemy.BigInteger, sqlalchemy.ForeignKey("users.id")
    )
    user = sqlalchemy.orm.relationship("User", back_populates="videos")

    comment_threads = sqlalchemy.orm.relationship(
        "CommentThread", back_populates="video"
    )

    @classmethod
    def from_raw_api_json(cls, data):
        """
        Create a video model from raw API data.

        Initialise a new Video() using a (JSON) dict as returned from the
        YouTube Data API (see EXAMPLE record above).
        """
        _data = {}
        _channel_data = {}

        _data["id"] = cls.integer_hash(data["id"]["videoId"])
        _channel_data["id"] = cls.integer_hash(data["snippet"]["channelId"])

        _data["title"] = data["snippet"]["title"]
        _data["description"] = data["snippet"]["description"]
        _data["published"] = dateparser.parse(data["snippet"]["publishedAt"])

        if not cls.pseudonymise_identifiers():
            _data["video_id"] = data["id"]["videoId"]
            _channel_data["channel_id"] = data["snippet"]["channelId"]
            _channel_data["title"] = data["snippet"]["channelTitle"]

        _data["channel"] = Channel(**_channel_data)

        _data["user"] = User(id=cls.integer_hash(data["snippet"]["channelId"]))

        return cls(**_data)

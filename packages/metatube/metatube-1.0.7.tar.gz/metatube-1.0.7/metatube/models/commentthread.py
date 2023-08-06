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

"""A YouTube comment thread ORM data model."""


__all__ = ["CommentThread"]


import dataclasses

import sqlalchemy

from .base import Base
from .comment import Comment
from .video import Video


# # EXAMPLE record
# {
#    "kind": "youtube#commentThread",
#    "etag": "\"SJZWTG6xR0eGuCOh2bX6w3s4F94/N-J1KPYA9h-RBd85_HSEeX3k8sw\"",
#    "id": "Ugw1hpNW--cMCwhG-wJ4AaABAg",
#    "replies": {
#     "comments": [
#      {
#       "kind": "youtube#comment",
#       "etag": "\"SJZWTG6xR0eGuCOh2bX6w3s4F94/uywljaTLRNTc5Xucl-OcyIF5dxs\"",
#       "id": "Ugw1hpNW--cMCwhG-wJ4AaABAg.90k0KongL2A93CeG-oebDs",
#       "snippet": {
#        "authorDisplayName": "Joko Prabowo",
#        "authorProfileImageUrl": "https://yt3.ggpht.com/...no-rj-mo",
#        "authorChannelUrl": "http://www.youtube.com/channel/UCZzay...",
#        "authorChannelId": {
#         "value": "UCZzaynt0Q3s3rEYEvWnCFKg"
#        },
#        "videoId": "wJitjtID0cc",
#        "textDisplay": "@Sugyono Saja betul om",
#        "textOriginal": "@Sugyono Saja betul om",
#        "parentId": "Ugw1hpNW--cMCwhG-wJ4AaABAg",
#        "canRate": true,
#        "viewerRating": "none",
#        "likeCount": 0,
#        "publishedAt": "2019-12-31T12:23:28.000Z",
#        "updatedAt": "2019-12-31T12:23:28.000Z"
#       }
#      },
#      {
#       "kind": "youtube#comment",
#       "etag": "\"SJZWTG6xR0eGuCOh2bX6w3s4F94/EwwgqCUTedRz4UQ0YrMDealtuec\"",
#       "id": "Ugw1hpNW--cMCwhG-wJ4AaABAg.90k0KongL2A90sDm4BCnYb",
#       "snippet": {
#        "authorDisplayName": "Sugyono Saja",
#        "authorProfileImageUrl": "https://yt3.ggpht.com/a/AGF-l7_eYs...j-mo",
#        "authorChannelUrl": "http://www.youtube.com/channel/UCVMHlmXv...",
#        "authorChannelId": {
#         "value": "UCVMHlmXvrgh-SASkqFy5nPw"
#        },
#        "videoId": "wJitjtID0cc",
#        "textDisplay": "Bikin burung laen drop. Suara kasar dan kerras",
#        "textOriginal": "Bikin burung laen drop. Suara kasar dan kerras",
#        "parentId": "Ugw1hpNW--cMCwhG-wJ4AaABAg",
#        "canRate": true,
#        "viewerRating": "none",
#        "likeCount": 1,
#        "publishedAt": "2019-11-03T11:36:28.000Z",
#        "updatedAt": "2019-11-03T11:36:28.000Z"
#       }
#      }
#     ]
#    }
#   }


@dataclasses.dataclass
class CommentThread(Base):
    """A YouTube comment thread ORM data model."""

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)

    comment_thread_id = sqlalchemy.Column(sqlalchemy.Text)

    video_id = sqlalchemy.Column(
        sqlalchemy.BigInteger, sqlalchemy.ForeignKey("videos.id")
    )
    video = sqlalchemy.orm.relationship("Video", back_populates="comment_threads")

    comments = sqlalchemy.orm.relationship("Comment", back_populates="comment_thread")

    @classmethod
    def from_raw_api_json(cls, data):
        """
        Create a video model from raw API data.

        Initialise a new Video() using a (JSON) dict as returned from the
        YouTube Data API (see EXAMPLE record above).
        """
        _data = {}

        _data["id"] = cls.integer_hash(data["id"])

        _data["comment_thread_id"] = data["id"]

        _data["video"] = Video(id=cls.integer_hash(data["snippet"]["videoId"]))

        _data["comments"] = []
        order_in_comment_thread = 0
        try:
            _data["comments"].append(
                Comment.from_raw_api_json(
                    data["snippet"]["topLevelComment"], order_in_comment_thread
                )
            )
            order_in_comment_thread += 1
        except KeyError:
            pass
        try:
            for comment in data["replies"]["comments"]:
                _data["comments"].append(
                    Comment.from_raw_api_json(comment),
                    order_in_comment_thread,
                )
                order_in_comment_thread += 1
        except KeyError:
            pass

        return cls(**_data)

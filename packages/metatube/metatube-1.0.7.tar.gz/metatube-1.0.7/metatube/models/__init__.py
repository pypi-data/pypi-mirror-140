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

"""ORM models for YouTube entities."""


__all__ = [
    "Channel",
    "Comment",
    "CommentThread",
    "User",
    "Video",
]


import sqlalchemy

from .channel import Channel
from .comment import Comment
from .commentthread import CommentThread
from .user import User
from .video import Video

from ..config import Config
from .base import Base

with Config() as config:
    if "connection_string" in config:
        engine = sqlalchemy.create_engine(config["connection_string"])
        Base.metadata.create_all(engine)
        del engine

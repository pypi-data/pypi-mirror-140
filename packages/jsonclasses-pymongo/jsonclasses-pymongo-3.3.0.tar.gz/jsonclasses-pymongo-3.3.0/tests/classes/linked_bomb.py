from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='linked')
class LinkedBomb:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    soldiers: list[LinkedSoldier] = types.listof('LinkedSoldier') \
                                         .linkedthru('bombs').cascade
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedSoldier:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    bombs: list[LinkedBomb] = types.listof('LinkedBomb') \
                                   .linkedthru('soldiers').cascade
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required

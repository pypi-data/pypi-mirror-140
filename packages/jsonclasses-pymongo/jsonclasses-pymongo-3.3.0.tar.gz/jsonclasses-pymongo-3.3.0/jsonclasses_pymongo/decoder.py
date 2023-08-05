from __future__ import annotations
from typing import Any, Optional, TypeVar, cast, TYPE_CHECKING
from datetime import date, timezone
from jsonclasses.types import Types
from jsonclasses.fdef import FStore, FType
from jsonclasses.mgraph import MGraph
from .utils import (ref_db_field_key, ref_db_field_keys)
if TYPE_CHECKING:
    from .query import BaseQuery
    from .pobject import PObject
    T = TypeVar('T', bound=PObject)


class Decoder:

    def decode_list(self,
                    value: list[Any],
                    cls: type[T],
                    types: Types,
                    graph: MGraph,
                    query: BaseQuery | None = None) -> Optional[list[Any]]:
        if value is None:
            return None
        item_types = types.fdef.item_types
        new_cls = item_types.fdef.raw_inst_types
        return ([self.decode_item(value=item, cls=new_cls,
                                  types=item_types,
                                  graph=graph,
                                  query=query)
                for item in value])

    def decode_dict(self,
                    value: dict[str, Any],
                    cls: type[T],
                    types: Types,
                    graph: MGraph) -> Optional[dict[str, Any]]:
        if value is None:
            return None
        item_types = types.fdef.item_types
        return {k: self.decode_item(value=v, cls=cls, types=item_types, graph=graph) for k, v in value.items()}

    def decode_item(self,
                    value: Any,
                    cls: type[T],
                    types: Types,
                    graph: MGraph,
                    query: BaseQuery | None = None) -> Any:
        if value is None:
            return value
        if types.fdef.ftype == FType.DATE:
            return date.fromisoformat(value.isoformat()[:10])
        elif types.fdef.ftype == FType.DATETIME:
            return value.replace(tzinfo=timezone.utc)
        elif types.fdef.ftype == FType.ENUM:
            if isinstance(types.fdef.enum_class, str):
                enum_cls = cast(type, types.fdef.enum_class)
                return enum_cls(value)
            else:
                enum_cls = cast(type, types.fdef.enum_class)
                return enum_cls(value)
        elif types.fdef.ftype == FType.LIST:
            return self.decode_list(value=value, cls=cls, types=types,
                                    graph=graph, query=query)
        elif types.fdef.ftype == FType.DICT:
            return self.decode_dict(value=value, cls=cls, types=types,
                                    graph=graph)
        elif types.fdef.ftype == FType.INSTANCE:
            return self.decode_instance(value=value, cls=cls, types=types,
                                        graph=graph, query=query)
        else:
            return value

    def decode_instance(self,
                        value: dict[str, Any],
                        cls: type[T],
                        types: Types,
                        graph: MGraph,
                        query: BaseQuery | None = None) -> Any:
        inst_id = str(value.get('_id')) if value.get('_id') is not None else None
        dest = graph.getp(cls, inst_id)
        exist = True
        if dest is None:
            dest = cls()
            exist = False
        for field in cls.cdef.fields:
            key = cls.pconf.to_db_key(field.name)
            if field.is_primary:
                if not exist:
                    setattr(dest, field.name, inst_id)
                    graph.put(dest)
            elif field.is_foreign_key_store:
                if value.get(key) is not None:
                    subquery = None
                    if query:
                        subquery = next((s.query for s in query.subqueries if s.name == field.name), None)
                    if isinstance(value.get(key), list):
                        t = field.fdef.item_types
                        new_cls = t.fdef.raw_inst_types
                        setattr(dest, field.name,
                                self.decode_list(
                                    value[key], new_cls, field.types, graph, subquery))
                    else:
                        new_cls = field.fdef.inst_cls
                        setattr(dest, field.name,
                                self.decode_instance(
                                    cast(dict[str, Any], value.get(key)),
                                    new_cls, field.types, graph, subquery))
            elif field.is_local_one_ref:
                if value.get(key) is not None:
                    subquery = None
                    if query:
                        subquery = next((s.query for s in query.subqueries if s.name == field.name), None)
                    new_cls = field.fdef.inst_cls
                    inst = self.decode_item(
                        value=value.get(key), types=field.types, cls=new_cls,
                        graph=graph, query=subquery)
                    setattr(dest, field.name, inst)
                ref_id = value.get(ref_db_field_key(field.name, cls=cls))
                rfk = field.ref_name
                setattr(dest, rfk, str(ref_id))
                if query and hasattr(query, '_final_pick'):
                    if rfk not in query._final_pick:
                        setattr(dest, rfk, None)
            elif field.is_local_many_ref:
                if value.get(key) is not None:
                    subquery = None
                    if query:
                        subquery = next((s.query for s in query.subqueries if s.name == field.name), None)
                    new_cls = field.fdef.inst_cls
                    setattr(dest, field.name,
                            self.decode_list(
                                value[key], new_cls, field.types, graph, subquery))
                saved_keys = value.get(ref_db_field_keys(field.name, cls))
                if saved_keys:
                    setattr(dest, field.ref_name, [str(k) for k in saved_keys])
            elif field.is_inst_field:
                new_cls = field.fdef.inst_cls
                setattr(dest, field.name, self.decode_item(
                    value=value.get(key), types=field.types, cls=new_cls,
                    graph=graph))
            else:
                if not exist and field.fdef.fstore != FStore.CALCULATED:
                    setattr(
                        dest,
                        field.name,
                        self.decode_item(value=value.get(key),
                                         types=field.types,
                                         cls=cls, graph=graph))
        # apply partial status
        if hasattr(query, '_final_pick'):
            setattr(dest, '_is_partial', True)
            setattr(dest, '_partial_picks', getattr(query, '_final_pick'))
        return dest

    def apply_unmodified_status(self, root: T,
                             graph: Optional[MGraph] = None) -> None:
        if graph is None:
            graph = MGraph()
        if graph.get(root) is not None:
            return
        graph.put(root)
        for field in root.__class__.cdef.fields:
            if field.is_inst_field:
                if getattr(root, field.name) is not None:
                    self.apply_unmodified_status(getattr(root, field.name), graph)
            elif field.is_list_inst_field:
                if getattr(root, field.name) is not None:
                    for item in getattr(root, field.name):
                        self.apply_unmodified_status(item, graph)
        root._mark_unmodified()

    def decode_root(self,
                    root: dict[str, Any],
                    cls: type[T],
                    graph: MGraph | None = None,
                    query: BaseQuery | None = None) -> T:
        if graph is None:
            graph = MGraph()
        types = Types().objof(cls)
        decoded = self.decode_instance(root, cls, types, graph, query)
        self.apply_unmodified_status(decoded)
        return decoded

    def decode_root_list(self,
                         root_list: list[dict[str, Any]],
                         cls: type[T],
                         graph: MGraph | None = None,
                         query: BaseQuery | None = None) -> list[T]:
        if graph is None:
            graph = MGraph()
        types = Types().objof(cls)
        results: list[T] = []
        for root in root_list:
            decoded = self.decode_instance(root, cls, types, graph, query)
            results.append(decoded)
        for result in results:
            self.apply_unmodified_status(result)
        return results

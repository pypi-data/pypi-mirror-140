import os
import re
from functools import lru_cache
from typing import List, Optional
from urllib.parse import urlparse

from pony import orm

db = orm.Database()


@lru_cache()
def compile_pattern(pattern: str, case_sensitive: bool):
    flags = 0 if case_sensitive else re.IGNORECASE
    return re.compile(pattern, flags=flags)


class Rule(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    label = orm.Required(str)
    meta = orm.Optional(orm.Json, nullable=True)

    # regex (expression or composite)
    pattern = orm.Optional(str, nullable=True)

    # literals
    name = orm.Optional(str, nullable=True)
    synonyms = orm.Optional(orm.StrArray, nullable=True)

    # flags
    is_composite = orm.Required(bool, sql_default=False)
    case_sensitive = orm.Required(bool, sql_default=False)
    ignore_punctuation = orm.Required(bool, sql_default=False)
    has_groups = orm.Required(bool, sql_default=False)

    @property
    def is_pattern(self):
        return not self.is_literal and not self.is_composite

    @property
    def is_literal(self):
        return self.name is not None

    def get_groups(self, text: str):
        if self.has_groups:
            pattern = compile_pattern(self.pattern, self.case_sensitive)
            match = pattern.match(text)
            return match.groupdict()

    @classmethod
    def create_entity(cls, rule_id: int, text: str, start: int, end: int):
        rule: Rule = Rule.select(lambda r: r.id == rule_id).first()
        groups = rule.get_groups(text)
        meta = {**(rule.meta or {}), **(groups or {})} or None

        entity = dict(
            label=rule.label,
            text=text,
            start=start,
            end=end,
            meta=meta,
        )

        if rule.name:
            entity["name"] = rule.name

        if rule.synonyms:
            entity["synonyms"] = rule.synonyms

        return entity


class Connection:
    def __init__(self, db_url: str = None):
        db_url = db_url or os.environ.get("ENTITYSCAN_DB_URL")
        db_bind_params = parse_url(db_url)

        table = db_bind_params.pop("_table_", False)
        if table:
            Rule._table_ = table

        db.bind(**db_bind_params)
        db.generate_mapping(create_tables=True)

    @classmethod
    def close(cls):
        db.disconnect()
        db.provider = None

    @orm.db_session
    def get_count(self):
        return Rule.select().count()

    @orm.db_session
    def delete(self):
        return Rule.select().delete()

    @orm.db_session
    def add_rule(
        self,
        label: str,
        pattern: Optional[str] = None,
        name: Optional[str] = None,
        synonyms: Optional[List[str]] = None,
        is_composite: bool = False,
        case_sensitive: bool = False,
        ignore_punctuation: bool = False,
        meta: dict = None,
    ):
        has_groups = "(?P<" in (pattern or "")

        return Rule(
            label=label,
            pattern=pattern,
            name=name,
            synonyms=synonyms,
            is_composite=is_composite,
            case_sensitive=case_sensitive,
            ignore_punctuation=ignore_punctuation,
            has_groups=has_groups,
            meta=meta,
        )


def parse_url(db_url: str):
    # generate arguments for database binding:
    # https://docs.ponyorm.org/firststeps.html#database-binding

    url = urlparse(db_url)
    assert url.scheme in {"sqlite", "postgres"}, f"Unsupported: {url.scheme}"

    kw = {"provider": url.scheme}
    path_parts = url.path.split("/")

    if url.scheme == "sqlite":
        if path_parts[1].startswith(":"):
            kw["filename"] = path_parts[1]
        else:
            kw["filename"] = "/".join(path_parts)

    # postgres://user:pass@host:port/database/schema.table
    if url.scheme == "postgres":
        kw["user"] = url.username or ""
        kw["password"] = url.password or ""
        kw["host"] = url.hostname or ""

        path_parts += ["", "", ""]
        kw["database"] = path_parts[1]

        schema = path_parts[2] or ""
        table = path_parts[3] or ""
        if schema and table:
            kw["_table_"] = (schema, table)

        assert kw["database"], f"No database name provided in URL {db_url}"

    return kw

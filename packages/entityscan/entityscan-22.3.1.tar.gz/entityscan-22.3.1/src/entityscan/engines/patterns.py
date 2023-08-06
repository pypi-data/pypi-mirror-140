from typing import Optional, Any

import hyperscan as hs

from entityscan import Rule


class State:
    def __init__(self, data: bytes, encoding: str):
        self.data = data
        self.encoding = encoding
        self.entities = []

    def __call__(
        self,
        rule_id: int,
        start: int,
        end: int,
        flags: int,
        context: Optional[Any],
    ):
        text = self.data[start:end].decode(self.encoding)
        entity = Rule.create_entity(rule_id, text, start, end)
        self.entities.append(entity)


class PatternEngine:
    def __init__(self, encoding: str = None):
        self.encoding = encoding or "UTF-8"
        self.hyperscan_db = hs.Database()
        self.patterns = []
        self.ids = []
        self.flags = []
        self.is_active = False

    def add_rule(self, rule: Rule):
        pattern: bytes = rf"\b{rule.pattern}\b".encode(self.encoding)
        self.patterns.append(pattern)
        self.ids.append(rule.id)
        flag = hs.HS_FLAG_SOM_LEFTMOST
        if not rule.case_sensitive:
            flag |= hs.HS_FLAG_CASELESS
        self.flags.append(flag)
        self.is_active = True

    def compile(self):
        if self.is_active:
            self.hyperscan_db.compile(
                expressions=self.patterns,
                ids=self.ids,
                elements=len(self.patterns),
                flags=self.flags,
            )

    def scan(self, text: str):
        entities = []
        if self.is_active:
            data: bytes = text.encode(self.encoding)
            state = State(data=data, encoding=self.encoding)
            self.hyperscan_db.scan(data, match_event_handler=state)
            entities = state.entities
        return entities

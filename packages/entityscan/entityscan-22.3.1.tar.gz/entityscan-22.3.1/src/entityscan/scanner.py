from pony import orm
from entityscan import Connection, Rule, engines


class Scanner:

    _scanner = None

    def __init__(
        self,
        db_url: str = None,
        connection: Connection = None,
        encoding: str = None,
    ):
        assert db_url or connection, "Missing both db url or connection."
        self.db_url = db_url
        self.connection = connection or Connection(db_url=db_url)
        self.encoding = encoding or "UTF-8"
        self.patterns = engines.PatternEngine(encoding=self.encoding)
        self.composites = engines.CompositeEngine()
        self.literals = engines.LiteralEngine()

    @classmethod
    def instance(cls, db_url: str, encoding: str = None):
        if not cls._scanner:
            cls._scanner = Scanner(db_url=db_url, encoding=encoding)
            cls._scanner.compile()
        else:
            assert db_url == cls._scanner.db_url, "Incongruent DB URL"
        return cls._scanner

    @orm.db_session
    def compile(self):
        # collect
        for rule in Rule.select():
            if rule.is_pattern:
                self.patterns.add_rule(rule)
            elif rule.is_composite:
                self.composites.add_rule(rule)
            elif rule.is_literal:
                self.literals.add_rule(rule)
            else:
                raise ValueError(f"Invalid rule: {rule.id}")

        # compile
        self.patterns.compile()
        self.literals.compile()

        return self

    @orm.db_session
    def scan(self, text: str, skip_composites: bool = False):
        entities = self.patterns.scan(text)
        entities += self.literals.scan(text)
        if not skip_composites:
            entities = self.composites.scan(text, entities)
        return entities

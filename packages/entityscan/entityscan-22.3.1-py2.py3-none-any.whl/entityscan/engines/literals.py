from itertools import chain
from dawg import IntCompletionDAWG
from entityscan import Rule


class LiteralEngine:
    def __init__(self):
        self.rules = []
        self.dawg = IntCompletionDAWG([])

    def add_rule(self, rule: Rule):
        self.rules.append((rule.name, rule.id))
        for synonym in rule.synonyms or []:
            self.rules.append((synonym, rule.id))

    def compile(self):
        self.dawg = IntCompletionDAWG(self.rules)

    def is_prefix(self, term: str):
        for _ in self.dawg.iterkeys(term):
            return True
        return False

    def get_entity(self, term: str, start: int = None, end: int = None):
        rule_id = self.dawg.get(term)

        if rule_id:
            start = start or 0
            end = end or len(term)
            return Rule.create_entity(rule_id, term, start, end)

    def scan(self, text: str):
        last = 0
        curr = 0
        prefixes = []
        entities = []

        for right in chain(text, "\0"):
            if not right.isalnum():
                next_prefixes = []
                for left in chain([last], prefixes):
                    term = text[left:curr]

                    entity = self.get_entity(term, left, curr)
                    if entity:
                        entities.append(entity)

                    if self.is_prefix(term):
                        next_prefixes.append(left)

                prefixes = next_prefixes
                curr += 1
                last = curr

            else:
                curr += 1

        return entities

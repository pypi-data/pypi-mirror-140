import re
from collections import defaultdict
from functools import reduce
from string import punctuation

from entityscan import Rule

# https://stackoverflow.com/a/64303618
Trie = lambda: defaultdict(Trie)


class CompositeFinder:
    def __init__(self, engine: "CompositeEngine", text: str, entities: list):
        self.engine = engine
        self.text = text
        self.entities = entities
        self.composites = []
        self.curr_prefixes = []
        self.next_prefixes = []

    def find(self):
        for this in self.entities:
            if self.engine.is_prefix((this,)):
                self.next_prefixes.append((this,))

            for prefix in self.curr_prefixes:
                t_start, p_end = this["start"], prefix[-1]["end"]
                dist = t_start - p_end

                if dist <= self.engine.max_dist:
                    self.next_prefixes.append(prefix)

                    span_exact = self.text[slice(p_end, t_start)]

                    span_clean = span_exact.strip(punctuation)
                    span_exact = span_exact.strip()
                    span_clean = span_clean.strip()

                    self.process_prefix(prefix, span_exact, this)
                    if span_exact and (span_clean != span_exact):
                        self.process_prefix(prefix, span_clean, this)

            self.curr_prefixes = self.next_prefixes
            self.next_prefixes = []

        return self.composites

    def process_prefix(self, prefix: tuple, span: str, this: dict):
        if span:
            prefix += (span,)

        prefix += (this,)

        if self.engine.is_prefix(prefix):
            self.next_prefixes.append(prefix)

        label = self.engine.get_end(prefix)
        if label:
            composite = self.make_composite(self.text, label, prefix)
            self.composites.append(composite)

    @classmethod
    def make_composite(cls, text, label, this_key):
        start, end = this_key[0]["start"], this_key[-1]["end"]
        entities = [item for item in this_key if isinstance(item, dict)]
        entity_count = sum(ent.get("entity_count", 1) for ent in entities)

        return {
            "label": label,
            "text": text[start:end],
            "start": start,
            "end": end,
            "entity_count": entity_count,
            "entities": entities,
        }


class CompositeEngine:

    # trie helpers

    END = object()

    def __init__(self):
        self.trie = Trie()
        self.max_dist = 1

    def __contains__(self, item):
        return item in self.trie

    def __getitem__(self, part: str):
        return self.trie.get(part)

    def __setitem__(self, parts: tuple, label):
        parts = [p["label"] if isinstance(p, dict) else p for p in parts]
        val = reduce(dict.__getitem__, parts, self.trie)
        val[self.END] = label

    def is_prefix(self, parts: tuple):
        val = self.reduce(parts)
        prefix_keys = val and (val.keys() - {self.END})
        return len(prefix_keys or []) > 0

    def get_end(self, parts: tuple):
        val = self.reduce(parts)
        return val and val.get(self.END)

    def reduce(self, parts: tuple):
        parts = [p["label"] if isinstance(p, dict) else p for p in parts]

        trie = self.trie
        for part in parts:
            # need to check first, because getting creates
            if part in trie:
                trie = trie.get(part)

            # if invalid, return None
            else:
                return None

        return trie

    # add composite pattern

    def add_rule(self, rule: Rule):
        parts, this_max_dist = self.to_parts(
            rule.pattern, rule.ignore_punctuation
        )
        self[parts] = rule.label
        self.max_dist = max(self.max_dist, this_max_dist)

    re_labels = re.compile(r"(@[A-Z_]+)")
    re_punctuation = re.compile(r"")

    @classmethod
    def to_parts(cls, pattern: str, ignore_punctuation: bool) -> tuple:
        parts = []
        prev = None
        max_dist = 0
        for match in cls.re_labels.finditer(pattern):
            # remove leading @
            label = match.group()[1:]

            # current
            curr = dict(start=match.start(), end=match.end(), label=label)

            # if not first
            if prev:
                span = pattern[prev["end"] : curr["start"]]
                max_dist = max(max_dist, len(span))

                if span and ignore_punctuation:
                    span = span.strip(punctuation)

                span = span.strip()

                if span:
                    parts.append(span)

            parts.append(curr["label"])
            prev = curr

        return tuple(parts), max_dist

    # scan

    @classmethod
    def any_overlap(cls, entity_0: dict, entity_1: dict):
        is_overlap = entity_0["start"] < entity_1["end"]
        is_overlap = is_overlap and (entity_1["start"] < entity_0["end"])
        return is_overlap

    @classmethod
    def entity_sort(cls, entity):
        return (
            (-1 * entity.get("entity_count", 1)),
            entity.get("start", 0),
            (-1 * entity.get("end", 0)),
        )

    def scan(self, text: str, entities: list) -> list:
        entities = sorted(entities, key=self.entity_sort)
        keep_going = True

        while keep_going:
            keep_going = False
            composites = CompositeFinder(self, text, entities).find()

            if composites:
                entities = self.filter_sub_entities(composites, entities)
                keep_going = True

        return entities

    def filter_sub_entities(self, composites, entities):
        next_entities = []
        composites = sorted(composites, key=self.entity_sort)
        seen_offsets = set()

        for composite in composites:
            off = set(range(composite["start"], composite["end"] + 1))

            if seen_offsets.isdisjoint(off):
                seen_offsets.update(off)
                next_entities.append(composite)

        for entity in entities:
            if entity.get("start") not in seen_offsets:
                next_entities.append(entity)

        return next_entities

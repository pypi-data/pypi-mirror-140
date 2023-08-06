# -*- coding:Utf-8 -*-
from __future__ import unicode_literals

from collections import Counter
import re
import unicodedata

from pybtex.style.labels import BaseLabelStyle
from pybtex.plugin import register_plugin

from dataclasses import dataclass, field
import sphinxcontrib.bibtex.plugin

from sphinxcontrib.bibtex.style.referencing import BracketStyle, PersonStyle
from sphinxcontrib.bibtex.style.referencing.author_year \
    import AuthorYearReferenceStyle
from sphinxcontrib.bibtex.style.referencing.label \
    import LabelReferenceStyle

from typing import Union

_nonalnum_pattern = re.compile('[^A-Za-z0-9 \-]+', re.UNICODE)

def bracket_style() -> BracketStyle:
    return BracketStyle(
        left='(',
        right=')',
    )

def person_style() -> PersonStyle:
    return PersonStyle(
        style='last',
        abbreviate=False,
        sep=' & ',
        sep2=None,
        last_sep=None,
        other=' et al',
    )

def _strip_accents(s):
    return "".join(
        (c for c in unicodedata.normalize('NFD', s)
            if not unicodedata.combining(c)))

def _strip_nonalnum(parts):
    """Strip all non-alphanumerical characters from a list of strings.
    >>> print(_strip_nonalnum([u"ÅA. B. Testing 12+}[.@~_", u" 3%"]))
    AABTesting123
    """
    s = "".join(parts)
    return _nonalnum_pattern.sub("", _strip_accents(s))

class ApaLabelStyle(BaseLabelStyle):
    def format_labels(self, sorted_entries):
        labels = [self.format_label(entry) for entry in sorted_entries]
        count = Counter(labels)
        counted = Counter()
        for label in labels:
            if count[label] == 1:
                yield label
            else:
                yield label + chr(ord('a') + counted[label])
                counted.update([label])

    def format_label(self, entry):
        label = "Anonymous"
        if 'author' in entry.persons:
            label = self.format_author_or_editor_names(entry.persons['author'])
        elif 'editor' in entry.persons:
            label = self.format_author_or_editor_names(entry.persons['editor'])
        elif 'organization' in entry.fields:
            label = entry.fields['organization']
            if label.startswith("The "):
                label = label[4:]

        if 'year' in entry.fields:
            return "{}, {}".format(label, entry.fields['year'])
        else:
            return "{}, n.d.".format(label)

    def format_author_or_editor_names(self, persons):
        if len(persons) == 1:
            return _strip_nonalnum(persons[0].last_names)
        elif len(persons) == 2:
            return "{} & {}".format(
                _strip_nonalnum(persons[0].last_names),
                _strip_nonalnum(persons[1].last_names))
        else:
            return "{} et al.".format(
                _strip_nonalnum(persons[0].last_names))

register_plugin('pybtex.style.labels', 'apa', ApaLabelStyle)

@dataclass
class ApaReferenceStyle(AuthorYearReferenceStyle):
    bracket_parenthetical: BracketStyle = field(default_factory=bracket_style)
    bracket_textual: BracketStyle = field(default_factory=bracket_style)
    bracket_author: BracketStyle = field(default_factory=bracket_style)
    bracket_label: BracketStyle = field(default_factory=bracket_style)
    bracket_year: BracketStyle = field(default_factory=bracket_style)
    person: PersonStyle = field(default_factory=person_style)

sphinxcontrib.bibtex.plugin.register_plugin(
    'sphinxcontrib.bibtex.style.referencing',
    'apastyle', ApaReferenceStyle)

def setup(app):
    return {
        'version': '1.0.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }

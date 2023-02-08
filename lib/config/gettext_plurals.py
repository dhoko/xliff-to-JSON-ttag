"""
Load gettext plurals configuration
==================================

From http://docs.translatehouse.org/projects/localization-guide/en/latest/l10n/pluralforms.html
Edit Kabyle from crowdin gettext output
"""
import json
from typing import Mapping
from pathlib import Path
from functools import lru_cache
from dataclasses import dataclass


@dataclass
class Plural:
    """map informations about a language and its plural"""

    rule: str
    name: str
    code: str


@lru_cache
def get_config() -> Mapping[str, Plural]:
    """Load gettext plurals config"""
    with open(Path("lib", "config", "gettext-plurals.json"), mode="r", encoding="utf-8") as source:
        content = json.load(source)
        return {code: Plural(code=code, **item) for code, item in content.items()}


def parse(locale: str) -> Plural:
    """Find the correct plural for a base language (first half of a locale ex: fr-FR -> fr)"""
    if "-" in locale or "_" in locale:
        code, _ = locale.replace("_", "-").split("-")
        return get_config()[code]
    return get_config()[locale]

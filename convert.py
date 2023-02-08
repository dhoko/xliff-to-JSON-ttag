"""
Convert XLIFF from Crowdin to TTag JSON (compact)
=================================================

Based on https://ttag.js.org/
"""
import os
import json
import logging
import argparse
from pathlib import Path
from typing import List, Mapping
from lib.helpers import read_xliff
from lib.translations import find_translations, Translation, UNTRANSLATED_TRANSLATION_STATE
from lib.config import gettext_plurals

logging.basicConfig(
    format="%(levelname)s:[%(filename)s] %(message)s",
    level=os.getenv("LOG_LEVEL", None) or logging.INFO,
)

parser = argparse.ArgumentParser(description="convert xliff to ttag JSON (compact)")
parser.add_argument(
    "--input",
    required=True,
    help="input xliff file",
)
parser.add_argument(
    "--output",
    required=True,
    help="output JSON file",
)
parser.add_argument(
    "--locale",
    required=True,
    help="locale from crowdin you're using",
)
args = parser.parse_args()

JsonTtag = Mapping[str, Mapping[str, Mapping[str, List[str]]]]


# ex: info["contexts"][entry.msgctxt][entry.msgid] = [entry.msgstr]
def sort_gettext_json(items: JsonTtag) -> JsonTtag:
    """
    Sort alphabetically the JSON made from the gettext
    so we can generate a better and consistant diff
    """

    def sort_map(
        items: Mapping[str, Mapping[str, List[str]]]
    ) -> Mapping[str, Mapping[str, List[str]]]:
        """
        Sort alphabetically a map
        """
        new_map = {}
        # OrderedDict(sorted(values.items(), str.lower) is not efficient for (<key>, [value]
        for item in sorted(items.keys(), key=str.lower):
            new_map[item] = items[item]
        return new_map

    for item in items["contexts"].items():
        (key, values) = item
        items["contexts"][key] = sort_map(values)

    items["contexts"] = sort_map(items["contexts"])
    return items


def clean_json(content: JsonTtag) -> JsonTtag:
    """Clean JSON empty keys and sort the json output"""
    # List all context without strings, so we can remove them from the final object
    keys = [key for (key, entries) in content["contexts"].items() if len(entries) == 0]
    for key in keys:
        del content["contexts"][key]

    return sort_gettext_json(content)


def is_broken_plural(translation: Translation) -> bool:
    """
    Detect a broken plural as it is going to break webapps
    A broken plural is an untranslated string version.
    """
    total = len(translation.string_with_states)
    if total == 1:
        return False

    total_broken = len(
        [
            item
            for item in translation.string_with_states
            if item[1] in UNTRANSLATED_TRANSLATION_STATE
        ]
    )

    return total_broken != total and total_broken > 0


def convert(file: Path, locale: str, output_path: Path) -> Path:
    """
    Convert a XLIFF file to the Ttag JSON format https://ttag.js.org/
    """

    (xliff, namespace) = read_xliff(file)

    info = {
        "headers": {
            "plural-forms": gettext_plurals.parse(locale).rule,
            "language": locale,
        },
        "contexts": {},
    }

    for translation in find_translations(xliff, namespace):
        map_info = info["contexts"].setdefault(translation.context, {})

        # Ignore a broken plural so we do not crash webapps
        if translation.is_plural and is_broken_plural(translation):
            continue

        map_info[translation.source] = translation.strings

    info = clean_json(info)

    with open(output_path, mode="w", encoding="utf-8") as output_json:
        output_json.write(json.dumps(info, indent=2, ensure_ascii=False))

    return output_path


def main():
    """main"""
    logging.info("convert %s to %s", args.input, args.output)
    convert(file=Path(args.input), output_path=Path(args.output), locale=args.locale)
    logging.info("done")


if __name__ == "__main__":
    main()

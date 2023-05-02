"""
Process translations inside xliff source file
============================================
"""
from dataclasses import dataclass, field
from typing import Tuple, List, Generator
from lxml import etree
from lib.helpers import is_tag

VALID_TRANSLATION_STATE = ("translated", "final")
UNTRANSLATED_TRANSLATION_STATE = "needs-translation"


@dataclass
class Translation:
    """
    Definition of a translation

    - `source`: english string to translate
    - `context`: Context of the string
    - `strings`: one of many translations available for the string
               many for plurals
    - `is_plural`: guess what
    - `occurrences`: list of source files + line number where we can find the source
    - `hash`: resname or id for a string
    """

    source: str
    context: str
    strings: List[str] = field(default_factory=list)
    string_with_states: List[Tuple[str, str]] = field(default_factory=list)
    occurrences: List[Tuple[str, str]] = field(default_factory=list)
    is_plural: bool = False
    hash: str = ""


def get_file_occurrences(text: str) -> List[Tuple[str, str]]:
    """
    Find occurrences informations about a string, as webapp xliff comes from
    a gettext file we store occurrences inisde the note tag.

    ex:

    <note>Context: Error
    Files:
    - packages/components/containers/contacts/widget/ContactsWidgetGroupsContainer.tsx:117</note>
    """
    if not "Files:" in text:
        return []

    sources = []
    files = text.split("Files:")[1]
    for source_file in files.split("\n"):
        if source_file.startswith("- "):
            file, line = source_file.split("- ")[1].strip().split(":")
            sources.append((file, line))

    return sources


def get_translation(node: etree._Element, namespace: str, all_states: bool = False) -> Translation:
    """Find all translations existing inside the document"""

    if is_tag(node, namespace, "trans-unit"):
        target = node.find(namespace + "target")
        source = node.find(namespace + "source")
        note = node.find(namespace + "note")

        # Only replace if the translation is approved or done
        if not target.get("state") in VALID_TRANSLATION_STATE and not all_states:
            return None

        return Translation(
            strings=[target.text],
            string_with_states=[(target.text, target.get("state"))],
            source=source.text,
            context=source.get("context"),
            occurrences=get_file_occurrences(note.text or ""),
            hash=node.get("resname"),
        )

    # How we define plurals for webapps
    if is_tag(node, namespace, "group"):
        note = node.find(namespace + "note")
        plurals = []
        plurals_states = []
        source_text = ""
        # Multiline format ex: Context: Error
        context = (
            note.text.split("\n")[0].strip().split("Context:")[1].strip()
            if note.text and "Context:" in note.text
            else ""
        )


        for unit in node:
            if is_tag(unit, namespace, "trans-unit"):
                if not source_text:
                    source = unit.find(namespace + "source")
                    source_text = source.text

                target = unit.find(namespace + "target")
                plurals_states.append((target.text, target.get("state")))
                # Only replace if the translation is approved or done
                if not target.get("state") in VALID_TRANSLATION_STATE and not all_states:
                    continue

                plurals.append(target.text)

        if len(plurals) == 0:
            return None

        return Translation(
            strings=plurals,
            source=source_text,
            context=context,
            hash=node.get("id"),
            string_with_states=plurals_states,
            is_plural=True,
            occurrences=get_file_occurrences(note.text),
        )
    return None


# pylint: disable=too-many-nested-blocks
def find_translations(
    xliff: etree._Element, namespace: str, all_states: bool = False
) -> Generator[Translation, float, str]:
    """
    Parse xliff file to find all translations available inside
    based on this definition: https://store.crowdin.com/xliff/
    Keep only valid translations
    """
    for node in xliff:
        for item in node:
            if not is_tag(item, namespace, "body"):
                continue

            for trans_unit in item:
                translation = get_translation(trans_unit, namespace, all_states=all_states)
                if translation:
                    yield translation


# pylint: disable=protected-access
# (File Node, Translation Unit node, string_id, Target Node, trans_unit container Node)
FileTranslationUnit = Tuple[etree._Element, etree._Element, str, etree._Element, etree._Element]


# pylint: disable=too-many-nested-blocks
def find_translations_node(
    xliff: etree._Element, namespace: str, file_iterator: bool = False
) -> Generator[FileTranslationUnit, float, str]:
    """
    Parse xliff file to find all translations node available inside
    based on this definition: https://store.crowdin.com/xliff/

    :warning: this method only list translations node, not care about if it's plural or not

    set `file_iterator=True` to yield only file by file (without translations)
    """
    for node in xliff:
        # Only yield the current file
        if file_iterator:
            yield node
            continue

        for item in node:
            if not is_tag(item, namespace, "body"):
                continue

            for trans_unit in item:
                if is_tag(trans_unit, namespace, "trans-unit"):
                    string_id = trans_unit.get("id") or trans_unit.get("resname")
                    target = trans_unit.find(namespace + "target")
                    yield (node, trans_unit, string_id, target, item)

                # How we define plurals for webapps
                if is_tag(trans_unit, namespace, "group"):
                    for unit in trans_unit:
                        if is_tag(unit, namespace, "trans-unit"):
                            string_id = unit.get("id") or trans_unit.get("resname")
                            target = unit.find(namespace + "target")
                            yield (node, unit, string_id, target, trans_unit)

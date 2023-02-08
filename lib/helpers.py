"""
Some helpers to process xliff content
====================================
"""
# pylint: disable=consider-using-f-string
from pathlib import Path
from typing import Tuple
from lxml import etree


def read_xml(file_path: Path, indent: str = "  ") -> etree._Element:
    """Read xml file with a custom indent and return a new xml object from lxml"""
    with open(file_path, mode="rb") as file:
        parser = etree.XMLParser(
            strip_cdata=False,
            remove_blank_text=False,
            remove_comments=False,
            resolve_entities=False,
        )
        root = etree.fromstring(file.read(), parser)
        etree.indent(root, space=indent)
        return root


def is_tag(node: etree._Element, namespace: str, tag: str) -> bool:
    """Get the tagname for XLIFF node as we have <namespace><tag>"""
    return node.tag.endswith("%s%s" % (namespace, tag))


def get_namespace(xliff: etree._Element) -> str:
    """All tags are behind this namepsace inside a XLIFF file"""
    return "{urn:oasis:names:tc:xliff:document:%s}" % xliff.get("version")


def read_xliff(file: Path) -> Tuple[etree.ElementTree, str]:
    """parse a file and return its xliff representation and its namespace"""
    xliff = read_xml(file)
    return (xliff, get_namespace(xliff))


def init_xliff(allow_nsmap: bool = False) -> etree._Element:
    """Generate new empty xliff"""
    nsmap = {None: "http://www.w3.org/XML/1998/namespace"}
    return etree.Element(
        "xliff",
        attrib={"version": "1.2", "xmlns": "urn:oasis:names:tc:xliff:document:1.2"},
        nsmap=nsmap if allow_nsmap else None,
    )

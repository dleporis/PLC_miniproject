#Import required library
import xml.etree.ElementTree as etree


def indent_xml(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent_xml(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

root = etree.fromstring("<fruits><fruit>banana</fruit><fruit>apple</fruit></fruits>""")
tree = etree.ElementTree(root)

indent_xml(root)
# writing xml
tree.write("example.xml", encoding="utf-8", xml_declaration=True)

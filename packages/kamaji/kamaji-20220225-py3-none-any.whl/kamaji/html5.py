#!/usr/bin/env python3
"""Kamaji Static Website Generator: HTML module
Copyright (C) 2022 Frank Abelbeck <kamaji@abelbeck.info>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
 
Development soundtrack:
   BBC Proms - Last Night 2019,
   Pet Shop Boys - Always on My Mind
"""

# import standard modules ("batteries included")
import pathlib
import xml.etree
import re

# import HTML5 parsing module (external dependency)
import html5lib

# regular expression for heading content extraction
RE_HEADING_STRIP = {
	"1": re.compile(r'''.*<h1.*?>(.*?)</h1>.*''',flags=re.DOTALL),
	"2": re.compile(r'''.*<h2.*?>(.*?)</h2>.*''',flags=re.DOTALL),
	"3": re.compile(r'''.*<h3.*?>(.*?)</h3>.*''',flags=re.DOTALL),
	"4": re.compile(r'''.*<h4.*?>(.*?)</h4>.*''',flags=re.DOTALL),
	"5": re.compile(r'''.*<h5.*?>(.*?)</h5>.*''',flags=re.DOTALL),
	"6": re.compile(r'''.*<h6.*?>(.*?)</h6>.*''',flags=re.DOTALL),
}

# protected tag elements
TAG_PROTECTED = frozenset.union(html5lib.constants.voidElements,html5lib.constants.cdataElements,html5lib.constants.rcdataElements)


def retrieveTitle(etreeDoc):
	"""Retrieve the first heading element content from the given xml.etree document.

All headings are probed from h1 to h6.

Args:
   etreeDoc: an xml.etree.ElementTree.Element or subclass instance.

Returns:
   A string, the heading content, supposedly the document title. If no content
   could be retrieved, the empty string is returned.
"""
	# check all h* headings from h1 to h6 and pick first match
	# as title of page
	for n in "123456":
		element = etreeDoc.find(f".//h{n}")
		if element is not None: break
	if element is not None:
		# tostring(): convert element to string, than extract content between heading tags
		return RE_HEADING_STRIP[n].sub(r'\1',xml.etree.ElementTree.tostring(element,encoding="unicode"))
	else:
		return ""


def removeEmptyNonvoidTags(element):
	"""Remove all empty subelements from the given element, recursively.

Elements listed in TAG_PROTECTED are not removed.

Args:
   element: an xml.etree.ElementTree.Element or subclass instance.
"""
	for subelement in element:
		try:
			if subelement.tag[0] == "{":
				# nameclassed element: skip, outside scope of this function
				continue
		except:
			pass
		if subelement.tag in TAG_PROTECTED:
			continue
		removeEmptyNonvoidTags(subelement)
		if len(subelement) == 0 and len("".join(subelement.itertext()).strip()) == 0:
			# element has no content, but should have: remove
			element.remove(subelement)


def processFragment(strContent,doRemoveEmptyTags=True):
	"""Process an HTML fragment and return the rendered HTML.

Args:
   strContent: a string containing HTML content.
   doRemoveEmptyTags: a boolean; if True (default), remove empty elements.

Returns:
   A string containing HTML content.
"""
	etreeFragment = html5lib.parseFragment(
		strContent,
		treebuilder="etree",
		namespaceHTMLElements=False
	)
	
	if doRemoveEmptyTags:
		# remove empty tags from tree
		# only do this with tags that normally come with content
		removeEmptyNonvoidTags(etreeFragment)
	
	walker = html5lib.getTreeWalker("etree")
	stream = walker(etreeFragment)
	s = html5lib.serializer.HTMLSerializer(
		inject_meta_charset=False,
		quote_attr_values="spec",
		quote_char='"',
		escape_lt_in_attrs=False,
		escape_rcdata=False,
		resolve_entities=True,
		strip_whitespace=False,
		minimize_boolean_attributes=True,
		use_trailing_solidus=False,
		space_before_trailing_solidus=True,
		sanitize=False,
		omit_optional_tags=False,
		alphabetical_attributes=False
	)
	return s.render(stream)
	

def parseString(strContent,strEncoding="utf-8",doRemoveEmptyTags=True,funProcessReference=lambda x:x):
	"""Process an HTML document and return the rendered HTML.

The given function is applied to all href/src elements.

Args:
   strContent: a string containing an HTML document.
   strEncoding: the charset applied to the output string.
   doRemoveEmptyTags: a boolean; if True (default), remove empty elements.
   funProcessReference: a function mapping a string to a string;
                        defaults to the identity function lambda x:x.

Returns:
   A string containing a processed HTML document.
"""
	etreeDoc = html5lib.parse(
		strContent,
		treebuilder="etree",
		namespaceHTMLElements=False
	)
	try:
		element = etreeDoc.find("./head/meta[@charset]")
		element.set("charset",strEncoding)
	except AttributeError:
		pass
	
	setKeys = set([key for element in etreeDoc.iter() for key in element.attrib.keys() if key.endswith(("href","src"))])
	for strAttrib in setKeys:
		for element in etreeDoc.findall(f".//*[@{strAttrib}]"):
			strRef = funProcessReference(element.get(strAttrib))
			if len(strRef) == 0:
				element.attrib.pop(strAttrib)
			else:
				element.set(strAttrib,strRef)
	
	strTitle = retrieveTitle(etreeDoc)
	
	if doRemoveEmptyTags:
		# remove empty tags from tree
		# only do this with tags that normally come with content
		removeEmptyNonvoidTags(etreeDoc)
	
	walker = html5lib.getTreeWalker("etree")
	stream = walker(etreeDoc)
	s = html5lib.serializer.HTMLSerializer(
		inject_meta_charset=True,
		quote_attr_values="spec",
		quote_char='"',
		escape_lt_in_attrs=False,
		escape_rcdata=False,
		resolve_entities=True,
		strip_whitespace=False,
		minimize_boolean_attributes=True,
		use_trailing_solidus=False,
		space_before_trailing_solidus=True,
		sanitize=False,
		omit_optional_tags=False,
		alphabetical_attributes=False
	)
	strContent = s.render(stream)
	
	return "<!DOCTYPE html>\n" + strContent,strTitle


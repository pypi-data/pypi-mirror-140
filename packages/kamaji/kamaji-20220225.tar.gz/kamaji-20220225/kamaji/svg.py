#!/usr/bin/env python3
"""Kamaji Static Website Generator: SVG processing module
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
import xml.etree.ElementTree
import io


def parseString(strContent,funProcessReference=lambda x:x):
	"""
Load the given XML string, apply given function to every xlink:href/src
attribute and return the modified XML string.

Args:
   strContent: a string of XML markup.
   funProcessReference: a function mapping a string to a string;
                        defaults to the identity function lambda x:x.
"""
	fContent = io.StringIO(strContent)
	return parse(fContent,funProcessReference)


def parse(pathFile,funProcessReference=lambda x:x):
	"""Load the given file, read and parse its XML contents, apply given function to
every xlink:href/src attribute and return the modified XML string.

Args:
   pathFile: a file stream as returned by open() or pathlib.Path.open().
   funProcessReference: a function mapping a string to a string;
                        defaults to the identity function lambda x:x.
"""
	# collect and register namespaces of the file
	dctNamespaces = { nsPrefix:nsUri for event,(nsPrefix,nsUri) in xml.etree.ElementTree.iterparse(pathFile, events=['start-ns']) }
	try:
		pathFile.seek(0)
	except AttributeError:
		pass
	for nsPrefix,nsUri in dctNamespaces.items():
		xml.etree.ElementTree.register_namespace(nsPrefix,nsUri)
	
	# parse file, now with correct namespaces
	etreeDoc = xml.etree.ElementTree.parse(pathFile).getroot()
	
	try:
		nsUriXlink = dctNamespaces["xlink"]
	except KeyError:
		# no xlink namespace: no xlink:href, so skip reference processing
		setReferences = set()
	else:
		# collect references
		setReferences = set()
		setKeys = set([key for element in etreeDoc.iter() for key in element.attrib.keys() if key.endswith(("href","src"))])
		for strAttrib in setKeys:
			for element in etreeDoc.iterfind(f".//*[@{strAttrib}]"):
				strRef = funProcessReference(element.get(strAttrib))
				if len(strRef) == 0:
					element.attrib.pop(strAttrib)
				else:
					element.set(strAttrib,strRef)
	
	strContent = xml.etree.ElementTree.tostring(etreeDoc,encoding="unicode")
	return strContent

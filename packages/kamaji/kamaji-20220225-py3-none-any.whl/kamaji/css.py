#!/usr/bin/env python3
"""Kamaji Static Website Generator: CSS processing module
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

# import CSS parsing module (external dependency)
import tinycss2


def traverseAST(cssContent,funProcessReference=lambda x:x):
	"""Traverse an abstract syntax tree and apply the given function to all
import/url() tokens.

Args:
   cssContent: a tinycss2.ast.Node or subclass instance.
   funProcessReference: a function mapping a string to a string;
                        defaults to the identity function lambda x:x.
"""
	if isinstance(cssContent,tinycss2.ast.URLToken):
		cssContent.value = funProcessReference(cssContent.value)
		cssContent.representation = cssContent.value
	elif isinstance(cssContent,tinycss2.ast.AtRule) and cssContent.at_keyword == "import":
		for token in cssContent.prelude:
			if isinstance(token,(tinycss2.ast.StringToken,tinycss2.ast.URLToken)):
				token.value = funProcessReference(token.value)
				token.representation = token.value
				break
	else:
		try:
			for rule in cssContent:
				traverseAST(rule,funProcessReference)
		except TypeError:
			pass
		try:
			for token in cssContent.prelude:
				traverseAST(token,funProcessReference)
		except (TypeError,AttributeError):
			pass
		try:
			for token in cssContent.content:
				traverseAST(token,funProcessReference)
		except (TypeError,AttributeError):
			pass


def parse(strContent,funProcessReference=lambda x:x):
	"""Parse given CSS content and apply given function to all import/url() tokens.

Args:
   strContent: a string with CSS content.
   funProcessReference: a function mapping a string to a string;
                        defaults to the identity function lambda x:x.
"""
	cssContent = tinycss2.parse_stylesheet(strContent)
	traverseAST(cssContent,funProcessReference)
	return tinycss2.serialize(cssContent)

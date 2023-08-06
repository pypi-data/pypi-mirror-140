#!/usr/bin/env python3
"""Kamaji Static Website Generator: BASh colourful markdown processing module
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
import html.parser
import textwrap
import re

# import own module: markdown
from . import md

# ANSI/V100 escape code parameters
NORMAL     = 0
BOLD       = 1
FAINT      = 2
ITALICS    = 3
UNDERLINED = 4
BLINK      = 5
STROKE     = 9

class BashMarkdownParser(html.parser.HTMLParser):
	"""A custom markdown parser, producing string output with BASh format codes.
"""
	
	RE_WS = re.compile("\s+")
	
	def __init__(self,language="en"):
		"""Constructor: create a new parser instance.

The provided language controls the markdown parser behaviour regarding quotes:

  language=de: Gänsefüßchen ‚‘ and „“
  language=fr: Guillemets ‹› and «»
  any other language: '' and ""

Args:
   language: a string; the language of the expected content.
"""
		super().__init__()
		self._md = md.Markdown(language)
		self.reset()
	
	def reset(self):
		"""Reset this parser instance. This clear the stacks, the output variable, and
the formatting counters.
"""
		super().reset()
		self._stack = []
		self._ol = []
		self._numPre = 0
		self._output = ""
		self._dctFormats = {
			BOLD       : 0,
			FAINT      : 0,
			ITALICS    : 0,
			UNDERLINED : 0,
			BLINK      : 0,
			STROKE     : 0
		}
	
	def pushFormat(self,*args):
		"""Set given format types and return the corresponding echo sequence.

Internally the corresponding format counters are increased. Depending on these
flags the echo sequence is constructed. Parameter 0 (reset all format
parameters) is always defined, any other parameter (like BOLD or ITALICS) is
added if the format counter is non-zero. Therefore '\\x1b[0m' is the shortest
possible return value.

Args:
   any argument of this function is assumed to be a number with a value of
   BOLD, FAINT, ITALICS, UNDERLINED, BLINK, or STROKE.

Returns:
   A echo format code string.
"""
		for idxFmt in args:
			try:
				self._dctFormats[idxFmt] = self._dctFormats[idxFmt] + 1
			except KeyError:
				pass
		return f'\x1b[{";".join(["0"]+[str(key) for key,value in self._dctFormats.items() if value > 0])}m'
	
	def popFormat(self,*args):
		"""Remove given format types and return the corresponding echo sequence.

Internally the corresponding format counters are decreased. Depending on these
flags the echo sequence is constructed. Parameter 0 (reset all format
parameters) is always defined, any other parameter (like BOLD or ITALICS) is
added if the format counter is non-zero. Therefore '\\x1b[0m' is the shortest
possible return value.

Args:
   any argument of this function is assumed to be a number with a value of
   BOLD, FAINT, ITALICS, UNDERLINED, BLINK, or STROKE.

Returns:
   A echo format code string.
"""
		for idxFmt in args:
			try:
				self._dctFormats[idxFmt] = max(self._dctFormats[idxFmt]-1, 0)
			except KeyError:
				pass
		return f'\x1b[{";".join(["0"]+[str(key) for key,value in self._dctFormats.items() if value > 0])}m'
	
	def parse(self,strMdContent):
		"""Parse given markdown content and return the BASh-formatted output string.

The parser is reset automatically beforehand.

Short formatting overview:
 - headings: BOLD and uppercase
 - code: FAINT
 - em: ITALICS
 - strong: BOLD
 - strike or del: STROKE
 - a: UNDERLINED

Args:
   strMdContent: a string containing markdown code.

Returns:
   A string.
"""
		self.reset()
		strContent,dctMeta,strToc,strTitle = self._md.convert(strMdContent)
		self.feed(strContent)
		self.close()
		return self._output
	
	def handle_starttag(self,tag,attrs):
		"""Overriden html.parser.HTMLParser.handle_starttag method.
"""
		self._stack.append("")
		if tag == "ol":
			self._ol.append(0)
		elif tag == "ul":
			self._ol.append(None)
		elif tag == "pre":
			self._numPre = self._numPre + 1
	
	def handle_endtag(self,tag):
		"""Overriden html.parser.HTMLParser.handle_endtag method.
"""
		data = self._stack.pop()
		if tag in ("h1","h2","h3","h4","h5","h6"):
			self._output = self._output + "\n" + self.pushFormat(BOLD) + data.upper() + self.popFormat(BOLD) + "\n\n"
		elif tag == "li":
			if self._ol[-1] is None:
				self._output = self._output + textwrap.fill(data,80,initial_indent=" * ",subsequent_indent="   ") + "\n"
			else:
				self._ol[-1] = self._ol[-1] + 1
				data = f"{self._ol[-1]:>3d}. {data}"
				self._output = self._output + textwrap.fill(data,80,initial_indent="",subsequent_indent="     ") + "\n"
		elif tag in ("ul","ol"):
			self._ol.pop()
			self._output = self._output + "\n"
		elif tag == "p":
			self._output = self._output + textwrap.fill(data,80) + "\n\n"
		elif tag == "pre":
			data = "\n".join([textwrap.fill(line,80,replace_whitespace=False,initial_indent="  ",subsequent_indent="  ") for line in data.splitlines()])
			self._output = self._output + data + "\n\n"
			self._numPre = max(self._numPre - 1, 0)
		elif tag == "code":
			self._stack[-1] = self._stack[-1] + self.pushFormat(FAINT) + data + self.popFormat(FAINT)
		elif tag in ("em","i"):
			self._stack[-1] = self._stack[-1] + self.pushFormat(ITALICS) + data + self.popFormat(ITALICS)
		elif tag == "span":
			self._stack[-1] = self._stack[-1] + data
		elif tag in ("strong","b"):
			self._stack[-1] = self._stack[-1] + self.pushFormat(BOLD) + data + self.popFormat(BOLD)
		elif tag in ("del","strike","s"):
			self._stack[-1] = self._stack[-1] + self.pushFormat(STROKE) + data + self.popFormat(STROKE)
		elif tag in ("a","u"):
			self._stack[-1] = self._stack[-1] + self.pushFormat(UNDERLINED) + data + self.popFormat(UNDERLINED)
		elif tag == "ins":
			self._stack[-1] = self._stack[-1] + self.pushFormat(FAINT,BOLD) + data + self.popFormat(FAINT,BOLD)
		elif tag in ("abbr","bdo","bdi","br","cite","data","dfn","em","kbd","mark","math","q","ruby","rt","rp","s","samp","small","span","strong","sub","sup","time","th","td","wbr"):
			# inline elements
			self._stack[-1] = self._stack[-1] + data
	
	def handle_data(self,data):
		"""Overriden html.parser.HTMLParser.handle_data method.
"""
		if self._numPre == 0:
			data = self.RE_WS.sub(" ",data)
		try:
			self._stack[-1] = self._stack[-1] + data
		except:
			pass



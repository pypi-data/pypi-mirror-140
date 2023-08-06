#!/usr/bin/env python3
"""Kamaji Static Website Generator: Markdown processing module
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
import re
import html
import xml.etree

# import python-markdown (external dependency)
import markdown
import markdown.extensions.codehilite
import markdown.extensions.meta
import markdown.extensions.sane_lists
import markdown.extensions.smarty
import markdown.extensions.toc
import markdown.extensions.abbr
import markdown.extensions.def_list
import markdown.extensions.fenced_code
import markdown.extensions.tables

# import own HTML5 module
from . import html5


class KamajiMarkdownTreeProcessor(markdown.treeprocessors.Treeprocessor):
	"""A custom Markdown Tree Processor.
"""
	RE_AMP_SUBSTITUTE = re.compile(r'''\x02amp\x03''')
	
	def __init__(self,*args,**kwargs):
		"""Constructor: initialise an instance.
"""
		super().__init__(*args,**kwargs)
		self._strTitle = ""
		self._funProcessReference = lambda x:x
	
	def run(self,root):
		"""Method that gets called when the tree of a Markdown document is processed.

This method applies the pre-defined reference processing function to all
href/src attributes in root and its subclass elements. In addition, it removes
the obfuscation code introduced by the markdown module and retrieves the
document title (=content of the first heading; cf. html5.retrieveTitle()).

Args:
   root: an xml.etree.ElementTree.Element or subclass instance.
"""
		#
		# collect href/src and first heading
		#
		# note: markdown obfuscates mail addresses from autolinks in the output, replacing each character with &#nnn;
		# autolink: <test@example.com>
		# the markdown module takes this even further by replacing & with \x02amp\x03 internally
		# it gets swapped back during postprocessing
		# thus \x02amp\x03 should be replaced in all reference strings
		#
		for strAttrib in ("href","src"):
			for element in root.findall(f".//*[@{strAttrib}]"):
				strRef = self._funProcessReference(self.RE_AMP_SUBSTITUTE.sub("&",element.get(strAttrib)))
				if len(strRef) == 0:
					element.attrib.pop(strAttrib)
				else:
					element.set(strAttrib,strRef)
		self._strTitle = html5.retrieveTitle(root)
	
	def setFunProcessReference(self,fun=lambda x:x):
		"""Set the reference processing function.

Args:
   fun: a function mapping a string to a string;
        defaults to the identity function lambda x:x.
"""
		self._funProcessReference = fun
	
	def getTitle(self):
		"""Return the title string. Obviously run() should have been called beforehand.
"""
		return self._strTitle


class KamajiMarkdownExtension(markdown.extensions.Extension):
	"""Custom markdown extension.

Implements the ~~delete~~/__insert__ syntax.

Enables href/src tracking/processing.
"""
	RE_SYNTAX_DEL = r'(~~)(.*?)~~'
	RE_SYNTAX_INS = r'(__)(.*?)__'
	
	def __init__(self,*args,**kwargs):
		"""Constructor: initialise an instance.
"""
		super().__init__(*args,**kwargs)
		self._funProcessReference = lambda x:x
	
	def extendMarkdown(self,md):
		"""Extension hook: register patterns for delete and insert syntax;
register the custom tree processor.
"""
		tagDel = markdown.inlinepatterns.SimpleTagPattern(self.RE_SYNTAX_DEL, "del")
		md.inlinePatterns.register(tagDel, "del", 75)
		
		tagIns = markdown.inlinepatterns.SimpleTagPattern(self.RE_SYNTAX_INS, "ins")
		md.inlinePatterns.register(tagIns, "ins", 76)
		
		self._treeProc = KamajiMarkdownTreeProcessor(md)
		self._treeProc.setFunProcessReference(self._funProcessReference)
		md.treeprocessors.register(self._treeProc,"KamajiTreeProcessor",5)
	
	def reset(self):
		"""Reset this instance: reset the custom tree processor.
"""
		try:
			self._treeProc.reset()
		except AttributeError:
			pass
	
	def getTitle(self):
		"""Return the title retrieved by the custom tree processor.

If no tree processor is defined, returns the empty string.
"""
		try:
			return self._treeProc.getTitle()
		except AttributeError:
			return ""
	
	def setFunProcessReference(self,fun=lambda x:x):
		"""Set the reference processing function.

In order for this to take effect, this has to be called before adding the
extension to the Markdown parser instance.

Args:
   fun: a function mapping a string to a string;
        defaults to the identity function lambda x:x.
"""
		self._funProcessReference = fun



class Markdown:
	"""Custom Markdown parser.

Enables the following standard extensions:
 - CodeHilite
 - Meta
 - SaneList
 - Smarty, with language-dependend quotes definitions
 - Toc, with marker disabled
 - Abbr
 - DefList
 - FencedCode
 - Table
 - Kamaji custom extension

SmartyPants configuration:
 - language=de: Gänsefüßchen ‚‘ and „“
 - language=fr: Guillemets ‹› and «»
 - any other language: quotes '' and ""
"""
	DCT_LANG_CFG_SMARTY = {
		"de": {
			"smart_angled_quotes": False,
			"substitutions": {
				'left-single-quote': '&sbquo;',
				'right-single-quote': '&lsquo;',
				'left-double-quote': '&bdquo;',
				'right-double-quote': '&ldquo;'
			}
		},
		"en": {
			"smart_angled_quotes": False,
			"substitutions": {}
		},
		"fr": {
			"smart_angled_quotes": True,
			"substitutions": {}
		}
	}
	
	def __init__(self,strLanguage="en"):
		"""Constructor: initialise an instance by generating a markdown.Markdown instance
and installing a set of extensions.

Args:
   strLanguage: a string defining the expected Markdown content language;
                defaults to "en".
"""
		self._mdExtCode = markdown.extensions.codehilite.CodeHiliteExtension()
		self._mdExtMeta = markdown.extensions.meta.MetaExtension()
		self._mdExtSaneLists = markdown.extensions.sane_lists.SaneListExtension()
		self._mdExtSmarty = markdown.extensions.smarty.SmartyExtension()
		self._mdExtToc = markdown.extensions.toc.TocExtension()
		self._mdExtToc.setConfig("marker","")
		self._mdExtAbbr = markdown.extensions.abbr.AbbrExtension()
		self._mdExtDefList = markdown.extensions.def_list.DefListExtension()
		self._mdExtFenced = markdown.extensions.fenced_code.FencedCodeExtension()
		self._mdExtTable = markdown.extensions.tables.TableExtension()
		self._mdExtKamaji = KamajiMarkdownExtension()
		
		if strLanguage != "en":
			self.setLanguage(strLanguage)
		
		self.regenerate()
	
	def regenerate(self):
		"""Regenerate the markdown.Markdown instance so that extension modifications can
take effect.
"""
		self._markdown = markdown.Markdown(
			output_format="html5",
			extensions=[
				self._mdExtCode,
				self._mdExtMeta,
				self._mdExtSaneLists,
				self._mdExtSmarty,
				self._mdExtToc,
				self._mdExtAbbr,
				self._mdExtDefList,
				self._mdExtFenced,
				self._mdExtTable,
				self._mdExtKamaji
			]
		)
	
	def convert(self,strMdSource,funProcessReference=lambda x:x):
		"""Convert Markdown content into HTML and return it.

Apply the given function to all href/src attributes.

Args:
   funProcessReference: a function mapping a string to a string;
                        defaults to the identity function lambda x:x.

Returns:
   A four-tuple (strContent,dctMeta,strToc,strTitle) with the HTML content
   string, a metadata dictionary, an HTML table of contents and a title string.
"""
		# record new reference recording function and reinitialise markdown instance
		self._mdExtKamaji.setFunProcessReference(funProcessReference)
		self.regenerate()
		# convert and process return values
		strContent = self._markdown.reset().convert(strMdSource)
		dctMeta = {key:"\n".join(value) for key,value in self._markdown.Meta.items()}
		strToc = self._markdown.toc
		strTitle = self._mdExtKamaji.getTitle()
		return strContent,dctMeta,strToc,strTitle
	
	def setLanguage(self,strLanguage):
		"""Set the document language.

This regenerates the SmartyPants extension. A call of regenerate() is advised.

Args:
   strLanguage: a string defining the expected Markdown content language;
                defaults to "en".
"""
		# smarty extension only updates substitutions config in extendMarkdown(),
		# thus any configuration changes after it needs to be re-created every time we change the config
		try:
			self._mdExtSmarty = markdown.extensions.smarty.SmartyExtension(**self.DCT_LANG_CFG_SMARTY[strLanguage])
		except KeyError:
			pass

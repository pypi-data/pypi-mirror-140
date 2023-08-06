#!/usr/bin/env python3
"""Kamaji Static Website Generator: Node management module
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
import urllib.parse # URI parsing in Node.new()
import os           # get current working directory
import os.path      # various path manipulation routines
import pathlib      # handle paths, write to and read from
import shutil       # copy files/trees
import codecs       # deal with encodings/charsets
import collections  # collections.ChainMap() as basis of the node environment
import time         # get current time
import zoneinfo     # parse timezone information
import datetime     # process file timestamp and date formats
import re           # various regular expression routines; finding/substituting variables
import html         # unescape HTML entities
import sys          # sys.exit() in case of module import errors
import json         # reading/writing Node hierarchy dumps
import inspect      # generate list of classes and class names

# import libmagic wrapper module (external dependency)
import magic # libmagic interface

# import graphviz wrapper module (external dependency)
import graphviz # create graph of references and dependencies

# import own modules
from . import md    # custom Markdown handling
from . import html5 # custom HTML5 handling
from . import svg   # custom SVG handling
from . import log   # custom logging module
from . import css   # custom CSS handling


#-------------------------------------------------------------------------------
# Node (root class)
#-------------------------------------------------------------------------------


class Node:
	"""Class for resource nodes.

This class records all instanciated nodes in a class-wide REGISTRY. The nodes
support hierarchical chaining and can be marked with various flags
(cf. MK_* contants).
"""
	MK_NONE         = 0b00000000000 # not marked
	MK_OUTDATED_DEP = 0b00000000001 # source file newer than dependency file
	MK_OUTDATED_OUT = 0b00000000010 # source file newer than output file
	MK_UPDATED_DEP  = 0b00000000100 # dependency file updated
	MK_UPDATED_OUT  = 0b00000001000 # output file updated
	MK_FAILED       = 0b00000010000 # processing failed
	MK_SKIPPED_DEP  = 0b00000100000 # file skipped as dependency (source is older)
	MK_SKIPPED_OUT  = 0b00001000000 # file skipped as reference (source is older)
	MK_TOUCHED_DEP  = 0b00010000000 # file touched as dependency
	MK_TOUCHED_OUT  = 0b00100000000 # file touched as reference
	MK_IGNORE       = 0b01000000000 # ignore during the build process
	MK_COPY         = 0b10000000000 # just copy during the build process
	
	REGISTRY = {}
	
	MAGIC = magic.Magic(mime=True,mime_encoding=True)
	
	PATH_DIR_OUT = pathlib.Path(".kamaji/out")
	
	SET_STR_PATHS_EXCLUDE = set()
	SET_STR_PATHS_INCLUDE = set()
	SET_STR_PATHS_COPY    = set()
	
	BOOL_FORCED = False
	
	def __init__(self,strUri):
		"""Constructor: initialise a Kamaji link node.

If node is given, this new node is put into a relationship with the given node.
The remaining arguments define this relationship and are ignored when no node
is given.

Args:
   strUri: a string or pathlib.Path instance.
"""
		self._strUri = str(strUri)
		self._setReferrers = set()
		self._setDependencies = set()
		self._setReferences = set()
		self._numMark = self.MK_NONE
		self.setPathDirOut(self.PATH_DIR_OUT)
	
	@classmethod
	def constructLocalPath(cls,strPathFile,strPathDirReference):
		"""Construct local path from given path, relative to the current working directory.

The following steps are taken:
 1) join strPathDirReference and strPathFile;
 2) normalise the result;
 3) get the canonical path;
 4) check that the result is a subpath of the current working directory;
 5) make the result relative to the current working directory.

Args:
   strPathFile: a string or pathlib.Path instance.
   strPathDirReference: a string or pathlib.Path instance; if None, the current 
                        working directory is used.

Returns:
   A string.

Raises:
   ValueError: either retrieving canonical path failed or resulting path is not
               a subpath of the current working directory.
"""
		try:
			strPathFile = os.path.realpath(
				os.path.normpath(
					os.path.join(
						strPathDirReference,
						strPathFile
					)
				)
			)
		except OSError as e:
			raise ValueError(f"retrieving canonical path of '{strPathFile}' failed") from e
		strPathCwd = os.getcwd()
		if os.path.commonpath((strPathCwd,strPathFile)) != strPathCwd:
			raise ValueError(f"path '{strPathFile}' is not a subpath of the current working directory")
		return os.path.relpath(strPathFile,strPathCwd)
	
	@classmethod
	def new(cls,strUri,strPathNodeReference="."):
		"""Fabricator: create a new instance base on the provided URI.

The URI is parsed with respect to the given referrer path.

Any HTML entities are converted to their corresponding Unicode characters.

Args:
   strUri: a string universally identifying the resource.
   strPathNodeReference: a string defining the path of the refering node;
                         defaults to the current working directory.

Returns:
   This is Node instance factory: Depending on the resource the URI is pointing
   to, an appropriate Node subclass is chosen, instantiated and returned.

Raises:
   ValueError: malformed or unsupported URI.
   Warning: unresolved address variable (there is a $ in the URI), or
            a document-internal reference.
"""
		strUri = html.unescape(str(strUri))
		
		# catch data URIs and strings with unresolved variables
		if strUri[0:5] == "data:":
			raise ValueError("URI scheme 'data' not supported")
		if "$" in strUri:
			raise Warning(f"unresolved address variable '{strUri}'")
		
		strScheme,strNetloc,strPath,strQuery,strFragment = urllib.parse.urlsplit(strUri)
		if strScheme == "file" or len(strScheme) == 0:
			#
			# local file URI (scheme=file or empty)
			#
			if len(strNetloc) == 0:
				scheme = ""
				if len(strPath) == 0:
					if len(strQuery) == 0 and len(strFragment) == 0:
						raise ValueError(f"empty URI not supported")
					else:
						raise Warning("document-internal reference")
				else:
					strPathNodeReference = str(strPathNodeReference)
					if os.path.isdir(strPathNodeReference):
						strPathDirReference = strPathNodeReference
					else:
						strPathDirReference = os.path.dirname(strPathNodeReference)
					strPathFile = cls.constructLocalPath(strPath,strPathDirReference)
				try:
					node = cls.REGISTRY[strPathFile]
				except KeyError:
					try:
						strMime,strCharset = [i.strip() for i in cls.MAGIC.from_file(strPathFile).split(";")]
						if strCharset[0:8] == "charset=":
							strCharset = strCharset[8:]
					except IsADirectoryError:
						node = NodeLocalDirectory(strPathFile)
					except (FileNotFoundError,PermissionError,OSError) as e:
						node = NodeLocalFileUnkown(strPathFile)
						#raise Warning(f"failed to determine MIME type of path {strPathFile} ({e})") from e
					else:
						if strMime == "text/html":
							node = NodeLocalFileHtml(strPathFile,strCharset)
						elif strMime == "text/markdown" or strMime == "text/plain" and strPathFile[-3:] == ".md":
							node = NodeLocalFileMarkdown(strPathFile,strCharset)
						elif strMime == "text/css" or strMime == "text/plain" and strPathFile[-4:] == ".css":
							node = NodeLocalFileCss(strPathFile,strCharset)
						elif strMime == "image/svg+xml":
							node = NodeLocalFileSvg(strPathFile,strCharset)
						else:
							node = NodeLocalFileMisc(strPathFile,strMime,strCharset)
					cls.REGISTRY[node.uri()] = node
			else:
				raise ValueError(f"file URI with explicit hostname '{strNetloc}' not supported")
		else:
			#
			# remote resource (non-empty scheme != file)
			# strip query and fragment string for core URI
			#
			strUriCore = urllib.parse.urlunsplit((strScheme,strNetloc,strPath,"",""))
			try:
				node = cls.REGISTRY[strUriCore]
			except KeyError:
				if strScheme == "mailto":
					node = NodeRemoteMailto(strUriCore)
				elif strScheme == "http" or strScheme == "https":
					node = NodeRemoteHttp(strUriCore)
				else:
					node = NodeRemoteMisc(strUriCore)
				cls.REGISTRY[node.uri()] = node
		
		# before returning the new node: establish link relationship with the referrer node
		if len(strQuery) > 0 or len(strFragment) > 0:
			node = NodeQuery(node,strQuery,strFragment)
		
		return node
	
	@classmethod
	def setPathsExclude(cls,*args):
		"""Set the paths of files/dirs that should be excluded from the build process.

This replaces the currently defined exclusion paths.

Args:
   Each argument is interpreted as a path or pattern string.
"""
		cls.SET_STR_PATHS_EXCLUDE = set([str(i) for i in args])
	
	@classmethod
	def setPathsInclude(cls,*args):
		"""Set the paths of files/dirs that should be included in the build process.

Inclusion overrides exclusion.

This replaces the currently defined exclusion paths.

Args:
   Each argument is interpreted as a path or pattern string.
"""
		cls.SET_STR_PATHS_INCLUDE = set([str(i) for i in args])
	
	
	@classmethod
	def setPathsCopy(cls,*args):
		"""Set the paths of files/dirs that should just be copied to output.

Copying overrides inclusion.

This replaces the currently defined exclusion paths.

Args:
   Each argument is interpreted as a path or pattern string.
"""
		cls.SET_STR_PATHS_COPY = set([str(i) for i in args])
	
	@classmethod
	def copyAllCopyPaths(cls):
		"""Copy all paths matched by the class-wide copy patterns.

Iterates over Node.SET_STR_PATHS_COPY and collects all matching files in the
current working directory. It then copies all matching files, recursively,
to the output directory if they are newer than their output pendant.

Erroneous patterns are ignored.
"""
		# collect all matching paths
		pathCwd = pathlib.Path()
		setPathsToCopy = set()
		for strPattern in cls.SET_STR_PATHS_COPY:
			try:
				setPathsToCopy.update(pathCwd.glob(strPattern))
			except ValueError as e:
				log.debug("error in pattern '%s' (%s)",strPattern,e)
		
		while setPathsToCopy:
			pathToCopy = setPathsToCopy.pop()
			pathToCopyOut = cls.PATH_DIR_OUT / pathToCopy
			NodeLocal.recordOutputFile(pathToCopyOut)
			if cls.BOOL_FORCED:
				doCopy = True
			else:
				try:
					doCopy = pathToCopy.stat().st_mtime > pathToCopyOut.stat().st_mtime
				except OSError:
					doCopy = True
			if doCopy:
				# copy pathToCopy to pathToCopyOut
				# recurse if necessary
				if pathToCopy.is_dir():
					setPathsToCopy.update(pathToCopy.glob("**/*"))
					setPathsToCopy.discard(pathToCopy)
					log.debug("added contents of directory '%s' to copy list",pathToCopy)
				else:
					try:
						pathToCopyOut.parent.mkdir(parents=True,exist_ok=True)
						shutil.copy2(pathToCopy,pathToCopyOut)
					except (OSError,shutil.Error) as e:
						log.error("error while copying file '%s' to '%s' (%s)",pathToCopy,pathToCopyOut,e)
					else:
						log.info("copied file '%s' to '%s'",pathToCopy,pathToCopyOut)
	
	@classmethod
	def determineMarkBuild(cls,path):
		"""Check if given path should be ignored, processed or copied.

Decision process:
   if path matches any exclude pattern then
      if path matches any include pattern then
         return value is MK_NONE
      else
         return value is MK_IGNORE
   if path matches any copy pattern then
      return value is MK_COPY

Thus copying overrides processing overrides ignoring.

Args:
   path: a pathlib.Path or subclass instance.

Returns:
   A number, either cls.MK_NONE, cls.MK_IGNORE, or cls.MK_COPY.

Raises:
   AttributeError: invalid argument (not a pathlib.Path or subclass instance).
"""
		retval = cls.MK_NONE
		for strPatternEx in cls.SET_STR_PATHS_EXCLUDE:
			if path.match(strPatternEx):
				retval = cls.MK_IGNORE
				for strPatternIn in cls.SET_STR_PATHS_INCLUDE:
					if path.match(strPattern):
						retval = cls.MK_NONE
						break
				break
		for strPattern in cls.SET_STR_PATHS_COPY:
			if path.match(strPattern):
				retval = cls.MK_COPY
				break
		return retval
	
	@classmethod
	def determineAndSetMarkBuild(cls,node,path):
		"""Mark the given node according to the class-wide exclude, include, and copy
pattern definitions.

This clears the MK_IGNORE and MK_COPY marks. It then sets the mark returned by
determineMarkBuild(path).

Args:
   node: a Node or subclass instance.
   path: a pathlib.Path or subclass instance; alternatively a path string.

Raises:
   AttributeError: invalid argument (either node is not a Node or subclass
                   instance or path is not a pathlib.Path or subclass instance).   
"""
		node.clearMark(cls.MK_IGNORE)
		node.clearMark(cls.MK_COPY)
		numMark = cls.determineMarkBuild(path)
		node.setMark(numMark)
	
	@classmethod
	def setPathDirOut(cls,pathDirOut):
		"""Set the class-wide output directory path.

Any missing directory components are created automatically.

Args:
   pathDirDep: a string or pathlib.Path instance.

Raises:
   FileExistsError: pathDirOut points to an existing file.
"""
		pathDirOut = pathlib.Path(pathDirOut)
		pathDirOut.mkdir(parents=True,exist_ok=True)
		cls.PATH_DIR_OUT = pathDirOut
	
	@classmethod
	def setForced(cls,boolForced=True):
		"""Set the class-wide forced mode flag.

In forced mode, isNeedingUpdate() and isNeedingUpdateDep() always return True.

Args:
   boolForced: a boolean.
"""
		cls.BOOL_FORCED = bool(boolForced)
	
	def uri(self):
		"""Return the URI of this node.

Returns:
   A string.
"""
		return self._strUri
	
	def setMark(self,mark):
		"""Mark this node.

If mark is not a number, the mark is not updated.

Args:
   mark: an integer; a combination of one or more MK_* constants.
"""
		try:
			self._numMark = self._numMark | mark
		except TypeError:
			pass
	
	def getMark(self):
		"""Return the current mark of this node as an integer.
"""
		return self._numMark
	
	def clearMark(self,mark=None):
		"""Clear the mark of this node.

If mark is not a number and not None, the mark is not updated.

If mark is None, the mark is reset to MK_NONE.

Args:
   mark: an integer, a combination of one or mode MK_* constants which should be
         removed from the node's mark.
"""
		if mark is None:
			self._numMark = self.MK_NONE
		else:
			try:
				self._numMark = self._numMark & ~mark
			except TypeError:
				pass
	
	def hasMark(self,mark):
		"""Return True if the node has the given mark.

Returns:
   A boolean. If mark is not a number, returns False.

Args:
   mark: an interger, a combination of one or mode MK_* constants.
"""
		try:
			return bool(self._numMark & mark)
		except TypeError:
			return False
	
	def hasFailed(self):
		"""Return True if this node is marked as "failed".
"""
		return bool(self._numMark & self.MK_FAILED)
	
	def wasProcessed(self):
		"""Return True if this node is marked as touched.
"""
		return bool(self._numMark & (self.MK_TOUCHED_DEP | self.MK_TOUCHED_OUT))
	
	def iterateReferrers(self):
		"""Return an iterator over all referrers of this node.
"""
		yield from self._setReferrers
	
	def hasReferrers(self):
		"""Return True if this node has at least one referrer.
"""
		return len(self._setReferrers) > 0
	
	def iterateReferences(self):
		"""Return an iterator over all referenced nodes of this node.
"""
		yield from self._setReferences
	
	def iterateDependencies(self):
		"""Return an iterator over all dependencies of this node.
"""
		yield from self._setDependencies
	
	def clearReferences(self):
		"""Remove all references of this node.
"""
		for node in self._setReferences:
			node.removeReferrer(self)
		self._setReferences.clear()
	
	def clearDependencies(self):
		"""Remove all dependencies of this node.
"""
		for node in self._setDependencies:
			node.removeReferrer(self)
		self._setDependencies.clear()
	
	def isReferencing(self,node):
		"""Return True if this node is referencing the given node.

Args:
   node: a Node or subclass instance.
"""
		return node in self._setReferences
	
	def isReferencedBy(self,node=None):
		"""Return True if this node is referenced by the given node.

If the given node is None, return True if this node is referenced by any node.

Args:
   node: a Node or subclass instance.
"""
		if node is None:
			for node in self._setReferrers:
				if node.isReferencing(self):
					return True
		else:
			return node.isReferencing(self)
	
	def isDependingOn(self,node):
		"""Return True if this node is depending on the given node.

Args:
   node: a Node or subclass instance.
"""
		return node in self._setDependencies
	
	def isDependencyOf(self,node=None):
		"""Return True if this node is a dependency of the given node.

If the given node is None, return True if this node is a dependency of any node.

Args:
   node: a Node or subclass instance.
"""
		if node is None:
			for node in self._setReferrers:
				if node.isDependingOn(self):
					return True
		else:
			return node.isDependingOn(self)
	
	def addReferrer(self,node):
		"""Add a referrer to this node.

Args:
   node: a Node or subclass instance.
"""
		if node is not None and node != self:
			self._setReferrers.add(node)
	
	def addLink(self,node,asDependency=False):
		"""Add a link to another node.

Args:
   node: a Node or subclass instance.
   asDependency: a boolean; if True, this node is added as dependency to the
                 referrer, otherwise it is added as a reference.
"""
		if node is not None and node != self:
			if asDependency:
				self._setDependencies.add(node)
				log.debug("added dependency '%s' to '%s'",node,self)
			else:
				self._setReferences.add(node)
				log.debug("added reference '%s' to '%s'",node,self)
			node.addReferrer(self)
	
	def addReference(self,node):
		"""Add a reference to this node.

Args:
   node: a Node or subclass instance.
"""
		self.addLink(node,asDependency=False)
	
	def addDependency(self,node):
		"""Add a dependency to this node.

Args:
   node: a Node or subclass instance.
"""
		self.addLink(node,asDependency=True)
	
	def removeReferrer(self,node):
		"""Remove given node from the list of referrers.

Args:
   node: a Node or subclass instance.
"""
		self._setReferrers.discard(node)
	
	def removeLink(self,node):
		"""Remove given node from the lists of references or dependencies.

Also removes this node from the given node's list of referrers.

Args:
   node: a Node or subclass instance.
"""
		self._setDependencies.discard(node)
		self._setReferences.discard(node)
		node.removeReferrer(self)
	
	@classmethod
	def removeNode(cls,node):
		"""Remove a node from the class registry.

This also removes the node from all existing nodes, either as referrer or
reference or dependency. If an existing node is deprived of all its referrers,
this node is removed, too.

Args:
   node: a Node or subclass instance; if None, all registered nodes are removed.

Returns:
   An integer, number of the nodes that where removed from the registry.
"""
		if node is None:
			nodes = set(cls.REGISTRY.values())
		else:
			try:
				nodes = set((cls.REGISTRY[node.uri()],))
			except KeyError:
				nodes = set()
		numNodes = 0
		while len(nodes) > 0:
			node = nodes.pop()
			if not node in cls.REGISTRY:
				continue
			# remove node as referrer from all dependencies
			# if a dependency has no referrers left, add it to list of nodes-to-remove
			for nodeDep in node.iterateDependencies():
				nodeDep.removeReferrer(node)
				if not nodeDep.hasReferrers():
					nodes.add(nodeDep)
			# remove node as referrer from all references
			# if a reference has no referrers left, add it to list of nodes-to-remove
			for nodeRef in node.iterateReferences():
				nodeRef.removeReferrer(node)
				if not nodeRef.hasReferrers():
					nodes.add(nodeRef)
			# remove node from all referrers
			for nodeRefr in node.referrers():
				nodeRefr.removeLink(node)
			del cls.REGISTRY[node.uri()]
			log.debug("removed node with URI '%s'",node.uri())
			numNodes = numNodes + 1
		return numNodes
	
	@classmethod
	def iterateRegistry(cls):
		"""Return an iterator over all nodes in the registry.
"""
		yield from cls.REGISTRY.values()
	
	@classmethod
	def cleanUpRegistry(cls):
		"""Remove all nodes that have no referrers.

Returns:
   An integer, number of the nodes that where removed from the registry.
"""
		numNodes = 0
		for node in cls.REGISTRY.values():
			if not node.hasReferrers():
				cls.removeNode(node)
				numNodes = numNodes + 1
		return numNodes
	
	@classmethod
	def clearRegistry(cls):
		"""Remove all nodes from the registry.

This is equivalent to calling removeNode(None).
"""
		cls.removeNode(None)
	
	def __hash__(self):
		"""Hash function: hash of the URI string.
"""
		return hash(self.uri())
	
	def __eq__(self,other):
		"""Equality: own URI and other URI are equal.

Args:
   other: a Node or subclass instance.

Returns:
   A boolean. If other is not a Node or subclass instance, returns False.
"""
		try:
			return self.uri() == other.uri()
		except AttributeError:
			return False
	
	def __ne__(self,other):
		"""Inequality: own URI and other URI are not equal.

Args:
   other: a Node or subclass instance.

Returns:
   A boolean. If other is not a Node or subclass instance, returns False.
"""
		try:
			return self.uri() != other.uri()
		except AttributeError:
			return False
	
	def __repr__(self):
		"""String conversion, eval-able: return construction expression
"""
		return f"{self.__class__.__name__}({self.uri()})"
	
	def __str__(self):
		"""String conversion: return string representation as follows.

	<class name string>: uri=<URI string> id=<instance ID>
"""
		return f"{self.__class__.__name__}: uri={self.uri()} id={id(self):x}"
	
	@classmethod
	def load(cls,pathFile):
		"""Load a node structure from the given JSON file.

This clears the class node registry and re-builds it with new nodes as specified
in the given dictionary. Then it establishes the links between the nodes.

Expected file format:
{
	stringURI : {
		"refs" : [list,of,URI,strings,...],
		"deps" : [list,of,URI,strings,...],
		"env"  : {key:value,...}
	},
	...
}

Args:
   pathFile: a string or pathlib.Path instance.

Raises:
   IsADirectoryError: invalid pathFile (is a directory).
   FileNotFoundError: pathFile does not exist.
   PermissionError: pathFile is not readable.
   ValueError: loading the JSON file failed.
"""
		# load file
		try:
			pathFile = pathlib.Path(pathFile)
			with pathFile.open() as f:
				dctNodes = json.load(f)
		except json.JSONDecodeError as e:
			raise ValueError(f"registry file '{pathFile}' corrupted ({e})") from e 
		else:
			log.debug("registry loading: successfully read JSON file '%s'",pathFile)
		
		cls.clearRegistry()
		
		# create nodes: this will populate the class
		try:
			for strUri,dctNode in dctNodes.items():
				try:
					node = cls.new(strUri)
				except ValueError as e:
					log.warning("registry loading: failed to create Node with URI '%s' (%s)",strUri,e)
				else:
					# create reference relationships
					try:
						for strPath in dctNode["refs"]:
							try:
								nodeRef = cls.new(strPath)
							except ValueError as e:
								log.warning("registry loading: failed to create Node with URI '%s' (%s)",strPath,e)
							else:
								node.addReference(nodeRef)
					except KeyError:
						# no dependencies defined: nevermind
						pass
					# create dependency relationships
					try:
						for strPath in dctNode["deps"]:
							try:
								nodeDep = cls.new(strPath)
							except ValueError as e:
								log.warning("registry loading: failed to create Node with URI '%s' (%s)",strPath,e)
							else:
								node.addDependency(nodeDep)
					except KeyError:
						# no dependencies defined: nevermind
						pass
					# environment processing: works only for subclasses NodeLocalFile and below
					try:
						node.importMetadata(dctNode["env"])
					except (AttributeError,KeyError):
						pass
		except AttributeError as e:
			raise ValueError("registry file '{pathFile}' is not a dictionary") from e
		
		# clean-up registry by removing orphaned nodes
		cls.cleanUpRegistry()
	
	@classmethod
	def dump(cls,pathFile):
		"""Convert the current node structure and the environment into a dictionary and
write it to the given JSON file.

Args:
   pathFile: a string or pathlib.Path instance.

Raises:
   ValueError: error while writing the file.
"""
		# iterate over nodes in registry, extract relevant information,
		# and write to json-encodable dictionary
		dctNodes = {}
		for node in cls.REGISTRY.values():
			dctNode = {}
			refs = [n.uri() for n in node.iterateReferences()]
			deps = [n.uri() for n in node.iterateDependencies()]
			
			if len(deps) > 0:
				dctNode["deps"] = deps
			
			if len(refs) > 0:
				dctNode["refs"] = refs
			
			try:
				dctNode["env"] = node.exportEnvironment()
			except AttributeError:
				pass
			
			dctNodes[node.uri()] = dctNode
			log.debug("registry dumping: exported Node with URI '%s'",node.uri())
		
		# save link database
		try:
			pathFile = pathlib.Path(pathFile)
			with pathFile.open("w") as f:
				json.dump(dctNodes,f)
		except IsADirectoryError as e:
			raise ValueError("registry file path '{pathFile}' is a directory") from e
		except PermissionError as e:
			raise ValueError("no permission to write registry file {pathFile}") from e
		else:
			log.debug("registry dumping: successfully wrote JSON file '%s'",pathFile)
	
	@classmethod
	def renderMap(cls, pathOut, boolDeps, boolRefs, boolUndirected, boolMerge, dctAttr, setClasses, setExclude, setInclude, strFormat, strEngine):
		"""Render a graph of the node relationships for the current Node registry.

Expected attribute dictionary format:
   {
      "graph": { key:value, ... }, # graph attributes
      "nodes": { key:value, ... }, # common node attributes
      "edges": { key:value, ... }, # common edge attributes
      "dep":   { key:value, ... }, # dependency edge attributes
      "ref":   { key:value, ... }, # reference edge attributes
      "Node":  { key:value, ... }, # node attributes for class "Node"
      "NodeLocal": { key:value, ... }, # node attributes for class "NodeLocal"
      ...
   }

Note: The suffix ".gv" is automatically added to pathOut in order to generate
the GraphViz source filename. Any existing last suffix is removed. The render
result filename is constructed by added a format-dependend suffix to the
source filename.

Args:
   pathOut: a pathlib.Path() or subclass instance.
   boolDeps: a boolean; if True, dependencies are drawn.
   boolRefs: a boolean; if True, references are drawn.
   boolUndirected: a boolean; if True, an undirected graph is rendered.
   boolMerge: a boolean; if True, parallel edges are merged.
   dctAttr: a dictionary with key-value attributes for graph, nodes, and edges.
   setClasses: a set of strings, defining the classes to consider.
   setExclude: a set of strings, defining file patterns to exclude.
   setInclude: a set of strings, defining file patterns to include;
               please note: inclusion overrides exclusion.
   strFormat: a string, name of the output format.
   strEngine: a string, name of the GraphViz engine.

Returns:
   A string; path to the file which was created.

Raises:
   ValueError: invalid argument (pathOut is a directory, unknown format or
               engine, unknown class name).
"""
		pathOut= pathlib.Path(pathOut).with_suffix(".gv")
		if pathOut.is_dir():
			raise ValueError(f"output path '{pathOut}' points to a directory.")
		
		# pre-process configuration arguments
		try:
			dctAttrGraph = dctAttr["graph"]
		except KeyError:
			dctAttrGraph = {}
		if boolMerge:
			dctAttrGraph["concentrate"] = "true"
		
		try:
			dctAttrNodes = dctAttr["nodes"]
		except KeyError:
			dctAttrNodes = {}
		try:
			dctAttrEdges = dctAttr["edges"]
		except KeyError:
			dctAttrEdges = {}
		
		try:
			dctAttrDeps = dctAttr["dep"]
		except KeyError:
			dctAttrDeps = {}
		dctAttrDeps["class"] = "edgedep"
		
		try:
			dctAttrRefs = dctAttr["ref"]
		except KeyError:
			dctAttrRefs = {}
		dctAttrRefs["class"] = "edgeref"
		
		dctAttrClasses = {}
		for strClass in setClasses:
			try:
				clsClass = DCT_NAME_TO_CLASS[strClass]
			except KeyError as e:
				raise ValueError(f"invalid class name '{strClass}'") from e
			else:
				try:
					dctAttrClasses[clsClass] = dctAttr[strClass]
				except KeyError:
					dctAttrClasses[clsClass] = {}
		tplClasses = tuple(dctAttrClasses.keys())
		
		setStrExclude = set([str(i) for i in setExclude])
		setStrInclude = set([str(i) for i in setInclude])
		
		# create the directed graph instance
		if boolUndirected:
			graph = graphviz.Graph("Kamaji",
				filename=pathOut.name,
				directory=pathOut.parent,
				graph_attr=dctAttrGraph,
				node_attr=dctAttrNodes,
				edge_attr=dctAttrEdges,
				format=strFormat,
				engine=strEngine
			)
		else:	
			graph = graphviz.Digraph("Kamaji",
				filename=pathOut.name,
				directory=pathOut.parent,
				graph_attr=dctAttrGraph,
				node_attr=dctAttrNodes,
				edge_attr=dctAttrEdges,
				format=strFormat,
				engine=strEngine
			)
		
		# node collection:
		#  1) iterate over registry
		#  2) if node is not instance of defined class set: ignore
		#  3) if local path node and matched by exclude pattern but not any include pattern: ignore
		#  4) obtain URI; if local path node, use path and make it relative to output directory
		#  5) record in list of nodes, map node to index, increment index
		dctNodeIndex = {}
		lstNodes = []
		i = 0
		for node in cls.REGISTRY.values():
			if isinstance(node,tplClasses):
				boolDoExclude = False
				try:
					pathNode = node.path()
				except AttributeError:
					strUri = node.uri()
				else:
					for strPatternEx in setStrExclude:
						if pathNode.match(strPatternEx):
							boolDoExclude = True
							for strPatternIn in setStrInclude:
								if pathNode.match(strPatternIn):
									boolDoExclude = False
									break
							break
					strUri = os.path.relpath(node.path(),pathOut.parent)
				try:
					strLabel = node.getVariable("titleContent",boolOnlyExplicit=True)
				except (AttributeError,KeyError):
					strLabel = node.uri()
				else:
					if len(strLabel) == 0:
						strLabel = node.uri()
				# if node should not be excluded and
				# it is not a dependency or dependencies should be displayed:
				# record node
				if not boolDoExclude and (not node.isDependencyOf() or boolDeps):
					lstNodes.append((node,strUri,strLabel))
					dctNodeIndex[node] = i
					i = i + 1
		
		# edge collection:
		#  1) iterate over node list
		#  2) if dependencies are requested, iterate over all dependencies and record in edge list (dep -> node)
		#  3) if references are requested, iterate over all reference and record in edge list (node -> ref)
		#  4) for every edge, memorise used node indizes in set of used nodes
		lstEdgesDep = []
		lstEdgesRef = []
		setNodesUsed = set()
		for node,i in dctNodeIndex.items():
			iDep = None
			iRef = None
			if boolDeps:
				for nodeDep in node.iterateDependencies():
					try:
						iDep = dctNodeIndex[nodeDep]
					except KeyError:
						pass
					else:
						lstEdgesDep.append((iDep,i))
						setNodesUsed.add(iDep)
			if boolRefs:
				for nodeRef in node.iterateReferences():
					try:
						iRef = dctNodeIndex[nodeRef]
					except KeyError:
						pass
					else:
						lstEdgesRef.append((i,iRef))
						setNodesUsed.add(iRef)
			if iDep is not None or iRef is not None:
				setNodesUsed.add(i)
		
		# node generation:
		#  1) iterate over set of used nodes
		#  2) prepare node class-specific attributes + URL
		#  3) add to graph
		for i in sorted(setNodesUsed):
			node,strUri,strLabel = lstNodes[i]
			dctAttrNode = {}
			for cls in type(node).__mro__:
				try:
					dctAttrNode = dctAttrClasses[cls]
				except KeyError:
					pass
			dctAttrNode["URL"] = strUri
			graph.node(f"n{i}",label=strLabel,**dctAttrNode)
		
		# edge generation: iterate over list of edges and add to graph
		for indexTail,indexHead in lstEdgesDep:
			graph.edge(f'n{indexTail}',f'n{indexHead}',**dctAttrDeps)
		for indexTail,indexHead in lstEdgesRef:
			graph.edge(f'n{indexTail}',f'n{indexHead}',**dctAttrRefs)
		
		return graph.render()
	
	def build(self,asDependency=False):
		"""Build this node.

This method is meant to be enhanced and only does the following:

   if node is marked with MK_IGNORE then
      no further building actions are allowed, return False
      
   else if node is built a a dependency and was not touched as a dependency then
      touch as dependency, return True
      
   else if node is built as a reference and was not touched as a reference then
      touch as reference, return True
      
   otherwise
      return False

The MK_IGNORE, MK_TOUCHED_DEP, and MK_TOUCHED_OUT marks are modified if needed.

If you override this method, call this implementation via super().build() and
check that it returns True before you proceed. If it returns False, you should
abord processing, since otherwise you might have run into a loop in the node
graph.

Args:
   asDependency: a boolean; if True, the node is build as a dependency.

Returns:
   A boolean. True if the node build process should proceed, False otherwise.
"""
		if self.hasMark(self.MK_IGNORE):
			# if MK_IGNORE is set, abort building process
			log.debug("ignoring node with URI '%s' as requested",self.uri())
			return False
		elif asDependency and not self.hasMark(self.MK_TOUCHED_DEP):
			# node as dependency not yet processed: mark as touched and return "proceed!"
			self.setMark(self.MK_TOUCHED_DEP)
			return True
		elif not asDependency and not self.hasMark(self.MK_TOUCHED_OUT):
			# node as reference not yet processed: mark as touched and return "proceed!"
			self.setMark(self.MK_TOUCHED_OUT)
			return True
		else:
			# node already processed, skip
			return False
	
	@classmethod
	def getStatistics(cls):
		"""Analyse the class registry and return the number of...

   ...nodes with mark 'updated';
   ...nodes with mark 'skipped';
   ...nodes with mark 'failed'.

Returns:
   A three-tuple (numUpdated,numSkipped,numFailed) of intergers.

"""
		numFailed = 0
		numUpdated = 0
		numSkipped = 0
		for node in cls.REGISTRY.values():
			if node.hasMark(cls.MK_FAILED):
				numFailed = numFailed + 1
			elif node.hasMark(cls.MK_UPDATED_OUT):
				numUpdated = numUpdated + 1
			elif node.hasMark(cls.MK_SKIPPED_OUT):
				numSkipped = numSkipped + 1
		return numUpdated,numSkipped,numFailed


#-------------------------------------------------------------------------------
# Node / Query
#-------------------------------------------------------------------------------


class NodeQuery(Node):
	"""Class for queries to and/or fragments of resources.

Query nodes only accept one other node as reference child during initialisation.
Most methods are redirected to this queried node.
"""
	def __init__(self,node,strQuery,strFragment):
		"""Constructor: initialise a query of a resource.

The node's URI is reconstructed from the node URI, strQuery and strFragment.

The MK_IGNORE mark is set per default.

Args:
   node: a Node or subclass instance; the queried node.
   strQuery: a query string in form "key1=value1&key2=value2...".
   strFragment: a fragment identifier string.
"""
		super().__init__(urllib.parse.urlunsplit(("","",node.uri(),strQuery,strFragment)))
		self.setMark(self.MK_IGNORE)
		# this node only accepts one child, as reference
		# methods for adding or removing nodes are disables
		# any referrer passed to this node is passed
		self._node = node
		self._strQuery = str(strQuery)
		self._strFragment = str(strFragment)
		super().addReference(node)
	
	def queriedNode(self):
		"""Return the queried node as Node or subclass instance.
"""
		return self._node
	
	def query(self):
		"""Return the query string.
"""
		return self._strQuery
	
	def fragment(self):
		"""Return the fragment string.
"""
		return self._strFragment
	
	def __getattr__(self,name):
		"""Let this class act as wrapper of the queried node's class.

Thus redirect all attributes not yet defined to the queried node.
"""
		return getattr(self._node,name)


#-------------------------------------------------------------------------------
# Node / Local (local resources)
#-------------------------------------------------------------------------------


class NodeLocal(Node):
	"""Abstract class for local resources.
"""
	SET_OUTPUT_FILES = set()
	
	def __init__(self,strPath,strMime,strMimeOut):
		"""Constructor: initialise a Kamaji local resource node.

Args:
   strPath: a string, path of the source file.
   strMime: a string, MIME type of the source file.
   strMimeOut: a string, MIME type of the output file.
"""
		super().__init__(strPath)
		self._path = pathlib.Path(strPath)
		self._strMime = str(strMime)
		self._strMimeOut = str(strMimeOut)
		self.determineAndSetMarkBuild(self,self._path)
	
	@classmethod
	def clearOutputFiles(cls):
		"""Clear the class-wide set of generated output files.
"""
		cls.SET_OUTPUT_FILES.clear()
	
	@classmethod
	def recordOutputFile(cls,pathFile):
		"""Record a file path in the class-wide set of generated output files.

Args:
   pathFile: a pathlib.Path instance or subclass instance.
"""
		cls.SET_OUTPUT_FILES.add(pathlib.Path(pathFile))
	
	@classmethod
	def isInOutputFileSet(cls,pathFile):
		"""Return True if given path is recorded in the class-wide set of output files.

Args:
   pathFile: a pathlib.Path instance or subclass instance.
"""
		return pathFile in cls.SET_OUTPUT_FILES
	
	def mime(self):
		"""Return the source file's MIME type string.
"""
		return self._strMime
	
	def mimeOut(self):
		"""Return the output file's MIME type string.
"""
		return self._strMimeOut
	
	def path(self):
		"""Return the source file path as pathlib.Path instance.
"""
		return self._path
	
	def pathOut(self):
		"""Return the output file path as pathlib.Path instance.
"""
		return self.PATH_DIR_OUT / self._path
	
	def timestamp(self):
		"""Return the source file timestamp as float of seconds since the Epoch.

Returns:
   A float; NaN if no timestamp could be obtained.
"""
		try:
			return self._path.stat().st_mtime
		except OSError:
			return float("NaN")
	
	def timestampOut(self):
		"""Return the output file timestamp as float of seconds since the Epoch.

Returns:
   A float; NaN if no timestamp could be obtained.
"""
		try:
			return self.pathOut().stat().st_mtime
		except OSError:
			return float("NaN")


#-------------------------------------------------------------------------------
# Node / Local / File
#-------------------------------------------------------------------------------


class NodeLocalFile(NodeLocal):
	"""Class for local files.
"""
	CHARSET_DEFAULT = "utf8"
	RE_VAR_NAME = re.compile(r'''[a-zA-Z0-9_-]+''',flags=re.IGNORECASE)
	CHAINMAP_DEFAULT = collections.ChainMap()
	DO_REMOVE_EMPTY_TAGS = True
	
	def __init__(self,strPath,strMime,strMimeOut,strCharset):
		"""Constructor: initialise a local file node.

Args:
   strPath: a string, path of the source file
   strMime: a string, MIME type of the source file.
   strMimeOut: a string, MIME type of the output file.
   strCharset: a string defining the charset to be used when reading the file.
"""
		super().__init__(strPath,strMime,strMimeOut)
		self._fltTimestampEnv = float("NaN")
		
		# note: output charset is always utf-8 for modified content; input encoding otherwise
		# sanitise charset: check against python's code database
		try:
			self._strCharset = codecs.lookup(strCharset).name
		except LookupError:
			self._strCharset = None # pathRead() will now return bytes
			log.warning("local file node with URI '%s' uses an unknown input charset '%s'",node.uri(),strCharset)
		
		# create new environment:
		# index.md defines environment for dir and its subdirs
		if self._path.name == "index.md":
			# this is an index file which defines a (sub)directory-wide environment
			# look for index.md of parent directories
			if self._path.parent == pathlib.Path():
				# already at top: parents list is empty, iteration will fall through to defaults
				pathParents = []
			else:
				# look up to the parent directory of this file's parent directory
				pathParents = self._path.parent.parents
		else:
			# not an index file: examine all its parents
			pathParents = self._path.parents
		
		try:
			# iterate over all parents found until an index file is found
			nodeIndex = None
			for pathParent in pathParents:
				try:
					nodeIndex = self.new(pathParent / "index.md")
				except ValueError:
					pass # non-existing file: ignore
				else:
					break # found an index file: terminate loop
			try:
				self._env = nodeIndex.getNewEnvironmentChild()
			except AttributeError:
				# nodeIndex is None, so no index file was found:
				# fall back to class-wide defaults
				self._env = self.CHAINMAP_DEFAULT.new_child()
		except TypeError:
			pass # pathParents is not iterable: it's None, env already set
	
	@classmethod
	def setEmptyTagRemoval(cls,doRemove=True):
		"""Set the empty tag removal flag.

Args:
   doRemove: a boolean; if True (default), empty HTML tags are removed.
"""
		cls.DO_REMOVE_EMPTY_TAGS = bool(doRemove)
	
	@classmethod
	def setDefaultVariable(cls,key,value):
		"""Set or overwrite a class-wide default environment variable.

Since variable names are processed case-independent, the variable name is
automatically cast to lower case.

Args:
   key: a string, the variable name.
   value: the variable's value.
"""
		cls.CHAINMAP_DEFAULT[str(key).lower()] = value
	
	@classmethod
	def clearDefaultVariable(cls,key):
		"""Remove a default variable from the class-wide default environment.

Since variable names are processed case-independent, the variable name is
automatically cast to lower case.

Non-existing variables are ignored.

Args:
   key: a string, the variable name.
"""
		try:
			del cls.CHAINMAP_DEFAULT[str(key).lower()]
		except KeyError:
			pass
	
	@classmethod
	def clearDefaultVariables(cls):
		"""Clear all default variables.
"""
		cls.CHAINMAP_DEFAULT.clear()
	
	def getNewEnvironmentChild(self):
		"""Derive a new child instance from this node's environment.

The new child instance will inherit all variables of this node's environment.

Returns:
   A collections.ChainMap instance.
"""
		return self._env.new_child()
	
	def importMetadata(self,dctMeta,strPathReference="."):
		"""Import a Metadata dictionary into this node's environment.

All path variables are assumed to be relative to the given path argument.

The dictionary keys should be strings. Since variable names are
case-insensitive, the dictionary keys are cast to lower-case. Non-strings
are ignored.

Special keys have a dollar sign $ as first character. For now, only '$tenv'
is parsed, leading to an updated environment timestamp.

Args:
   dctMeta: a dictionary.
   strPathReference: a string or pathlib.Path instance; defaults to ".".
"""
		dctMetaSane = {}
		for key,value in dctMeta.items():
			try:
				key = key.lower()
			except AttributeError:
				continue # skip invalid keys
			if key[0] == "$":
				# intercept special keys (used internally)
				if key == "$tenv":
					# special key: timestamp of this metadata/environment
					try:
						self._fltTimestampEnv = float(value)
					except:
						pass
				else:
					dctMetaSane[key] = value
			
			elif self.RE_VAR_NAME.fullmatch(key) is None:
				# key not matched by RE_VAR_NAME: invalid key name
				log.warning("metadata import: name '%s' is not a valid identifier",key)
			
			elif key[0:4] == "path":
				#
				# path variable: create new node from value; ignore erroneous paths
				#
				suffix = key[4:]
				try:
					nodePath = self.new(value,strPathNodeReference=str(strPathReference))
				except (ValueError,Warning) as e:
					log.warning("metadata import: variable '%s' references invalid path '%s' (%s)",key,self.path().parent / value,e)
				else:
					if isinstance(nodePath,NodeLocalFile):
						try:
							dctMetaSane["type" + suffix] = nodePath.mime()
						except AttributeError:
							log.warning("metadata import: variable '%s' references path '%s' without MIME data",key,nodePath.path())
						else:
							dctMetaSane[key] = nodePath
							self.addDependency(nodePath)
					else:
						log.warning("metadata import: variable '%s' references a non-local path '%s'",key,nodePath.uri())
			
			elif key == "timezone":
				#
				# timezone variable: get timezone; ignore if erroneous
				#
				try:
					dctMetaSane[key] = zoneinfo.ZoneInfo(value)
				except zoneinfo.ZoneInfoNotFoundError:
					log.warning("metadata import: unknown timezone '%'",value)
			
			elif key == "createtoc":
				#
				# createToc variable: interpret as boolean with True=1|y|yes
				#
				try:
					# case 1: loading metadata from markdown, so everything is a string --> parse string
					dctMetaSane[key] = value.lower() in ("y","yes","1","true")
				except AttributeError:
					# case 2: loading from JSON file --> value was already parsed, make sure it is a boolean
					dctMetaSane[key] = bool(value)
			
			else:
				#
				# any other variable: just import unaltered
				#
				dctMetaSane[key] = value
		
		self._env.clear()
		self._env.update(dctMetaSane)
	
	def exportEnvironment(self):
		"""Export this node's environment.

The environment timestamp is converted to the dictionary entry '$tenv'.

Timezone and path variable values are converted to strings.

Returns:
   A dictionary.
"""
		dctEnv = {}
		for key,value in self._env.maps[0].items():
			if isinstance(value,zoneinfo.ZoneInfo):
				dctEnv[key] = str(value)
			elif isinstance(value,Node):
				dctEnv[key] = value.uri()
			else:
				dctEnv[key] = value
		dctEnv["$tenv"] = self.timestampEnvironment()
		return dctEnv
	
	@classmethod
	def exportDefaults(cls):
		"""Export the class-wide default variables.

Timezone and path variable values are converted to strings.

Returns:
   A dictionary.
"""
		dctEnv = {}
		for key,value in self.CHAINMAP_DEFAULT.items():
			if isinstance(value,zoneinfo.ZoneInfo):
				dctEnv[key] = str(value)
			elif isinstance(value,nodes.Node):
				dctEnv[key] = value.uri()
			else:
				dctEnv[key] = value
		return dctEnv
	
	def setVariable(self,key,value):
		"""Set the value of an environment variable of this node.

Args:
   key: a string; invalid keys are ignored; cast to lower-case.
   value: any reasonable value.
"""
		try:
			self._env[key.lower()] = value # since markdown meta is case-insensitive, cast to lower
		except AttributeError:
			pass
	
	def getVariable(self,key,boolOnlyExplicit=False):
		"""Get the value of an environment variable of this node.

Args:
   key: a string; invalid keys are ignored; cast to lower-case.
   boolOnlyExplicit: a boolean; if True, only take explicitly declared variables
                     of this node into account and ignore inherited variables;
                     defaults to False.

Returns:
   A value.
"""
		try:
			key = key.lower()
		except AttributeError:
			pass
		else:
			if boolOnlyExplicit:
				return self._env.maps[0][key.lower()]
			else:
				return self._env[key.lower()]
	
	def clearVariable(self,key):
		"""Clear the given variable, i.e. remove it from the environment.

This affects only variables explicitly declared for this node. Inherited
variables are not affected. Unexisting variables are ignored.

Args:
   key: a string; invalid keys are ignored; cast to lower-case.
"""
		try:
			del self._env[key.lower()]
		except (AttributeError,KeyError):
			pass
	
	def clearVariables(self,key):
		"""Clear all variables, i.e. clear the environment.

This affects only variables explicitly declared for this node. Inherited
variables are not affected.
"""
		self._env.clear()
	
	def charset(self):
		"""Return the charset string used for source file decoding.
"""
		return self._strCharset
	
	def timestampEnvironment(self):
		"""Return the environment timestamp as float of seconds since the Epoch.

Returns:
   A float or NaN if no timestamp is set.
"""
		return self._fltTimestampEnv
	
	def setTimestampEnvironment(self,fltValue=None):
		"""Set the environment timestamp.

This also clears the MK_OUTDATED_DEP mark and sets the MK_UPDATED_DEP mark.

Args:
   fltValue: a float, seconds since the Epoch. If None (default) or not castable
             to float, the current time as returned by time.time() is used.
"""
		try:
			self._fltTimestampEnv = float(fltValue)
		except TypeError as e:
			# fltValue most likely not defined: fall back to current time
			self._fltTimestampEnv = time.time()
		self.clearMark(self.MK_OUTDATED_DEP)
		self.setMark(self.MK_UPDATED_DEP)
	
	def pathRead(self,applyCharset=True):
		"""Read the source file and return the contents.

The MK_FAILED mark is modified if needed.

Args:
   applyCharset: a boolean; if True (default), the file contents are decoded
                 using the predefined charset.

Returns:
   A bytes instance if no charset was defined or applyCharset is set to False;
   a str instance if charset was defined or applyCharset is set to True.

Raises:
   ValueError: an error occurred.
"""
		self.setMark(self.MK_FAILED)
		try:
			bytesContent = self.path().read_bytes()
		except IsADirectoryError as e:
			raise ValueError(f"could not read file {self.path()}: is a directory") from e
		except FileNotFoundError as e:
			raise ValueError(f"could not read file {self.path()}: file not found") from e
		except PermissionError as e:
			raise ValueError(f"could not read file {self.path()}: no permission") from e
		except OSError as e:
			raise ValueError(f"could not read file {self.path()}: {e}") from e
		if applyCharset and self._strCharset is not None:
			try:
				retval = bytesContent.decode(self._strCharset)
			except UnicodeDecodeError as e:
				raise ValueError(f"could not read file {self.path()}: invalid encoding {self._strCharset}") from e
		else:
			retval = bytesContent
		self.clearMark(self.MK_FAILED)
		return retval
	
	def pathOutWrite(self,data):
		"""Write given content to the output file.

The MK_FAILED, MK_OUTDATED_OUT and MK_UPDATED_OUT marks are modified if needed.

Args:
   data: either a bytes or a str instance; strings will be encoded using the
         internal default charset (utf-8).

Raises:
   ValueError: an error occurred.
"""
		self.setMark(self.MK_FAILED)
		try:
			self.pathOut().parent.mkdir(parents=True,exist_ok=True)
		except FileExistsError as e:
			raise ValueError(f"could not write file '{self.pathOut()}': given parent directory '{self.pathOut().parent}' is an existing file") from e
		try:
			data = data.encode(self.CHARSET_DEFAULT)
		except AttributeError:
			# data is not a string, try bytes
			try:
				data = bytes(data)
			except (TypeError,ValueError) as e:
				# data given neither as string nor bytes
				raise ValueError(f"could not write file {self.pathOut()}: given data is neither string nor bytes") from e
		except UnicodeDecodeError as e:
			raise ValueError(f"could not write file {self.pathOut()}: invalid encoding {self._strCharset}") from e
		
		try:
			self.pathOut().write_bytes(data)
		except IsADirectoryError as e:
			raise ValueError(f"could not write file {self.pathOut()}: is a directory") from e
		except FileNotFoundError as e:
			raise ValueError(f"could not write file {self.pathOut()}: file not found") from e
		except PermissionError as e:
			raise ValueError(f"could not write file {self.pathOut()}: no permission") from e
		except OSError as e:
			raise ValueError(f"could not write file {self.pathOut()}: {e}") from e
		self.clearMark(self.MK_FAILED)
		self.setMark(self.MK_UPDATED_OUT)
		self.clearMark(self.MK_OUTDATED_OUT)
	
	def isNeedingUpdateDep(self):
		"""Return True if the environment data is older than the source file.

The MK_OUTDATED_DEP mark is modified if needed.

The class-wide BOOL_FORCED variable overrides the timestamp evaluation. If True,
this method immediately returns True.
"""
		# 1) assume node is outdated; set mark and return True immediately if proof is found
		self.setMark(self.MK_OUTDATED_DEP)
		# 2) forced build: return immediately
		if self.BOOL_FORCED:
			return True
		# 3) check if source is newer than output
		if self._fltTimestampEnv != self._fltTimestampEnv or self.timestamp() > self._fltTimestampEnv:
			# if tEnv is defined (NaN is never equal to itself) or
			# source is newer than environment: needs dep update
			return True
		else:
			# clear mark and return false
			self.clearMark(self.MK_OUTDATED_DEP)
			return False
	
	def isNeedingUpdate(self):
		"""Return True if the output file is older than the source file.

The MK_OUTDATED_OUT and MK_SKIPPED_OUT marks are modified if needed.

The class-wide BOOL_FORCED variable overrides the timestamp evaluation. If True,
this method immediately returns True.
"""
		# 1) as we are debating whether to build or not, record an output file (either processed or skipped)
		self.recordOutputFile(self.pathOut())
		# 2) assume node is outdated; set mark and return True immediately if proof is found
		self.setMark(self.MK_OUTDATED_OUT)
		# 3) forced build: return immediately
		if self.BOOL_FORCED:
			return True
		# 4) check if source is newer than output
		try:
			t = self.timestampOut()
			if t != t or self.timestamp() > t:
				return True
		except FileNotFoundError:
			# output does not exist, thus needs update
			return True
		# 5) at this point, output seems up-to-date;
		#    but a dependency might have changed:
		#    compare timestamp of dependencies with timestamp of output
		for nodeDep in self.iterateDependencies():
			try:
				if nodeDep.timestamp() > t:
					return True
			except (OSError,FileNotFoundError,PermissionError):
				return True
		# 6) no dependency is newer than output and output is newer than source:
		#    clear mark (cf. 0)) and return False (no update needed)
		self.clearMark(self.MK_OUTDATED_OUT)
		self.setMark(self.MK_SKIPPED_OUT)
		return False
	
	def copyToOut(self):
		"""Create the output file by copying the source file.

Raises:
   OSError: writing output file failed.
   shutil.SameFileError: source and dependency file are the same file.
"""
		self.setMark(self.MK_FAILED)
		self.pathOut().parent.mkdir(parents=True,exist_ok=True)
		shutil.copy2(self.path(),self.pathOut())
		self.clearMark(self.MK_OUTDATED_OUT)
		self.setMark(self.MK_UPDATED_OUT)
		self.clearMark(self.MK_FAILED)
	
	def recordReference(self,strRef):
		"""Record a reference resource of this node and return the resource URI.

Since the URI is fed to new(), local paths are made relative to the current
working directory.

Args:
   strRef: a string, identifying universally the referenced resource.

Returns:
   A string; the URI of the resource, modified.
"""
		# create new node; the constructor will deal with local/remote resources
		# and URI unescaping
		try:
			nodeRef = self.new(strRef,strPathNodeReference=self.path())
		except ValueError as e:
			log.warning("erroneous reference '%s' (%s)",strRef,e)
			strUri = strRef
		except Warning:
			# unresolved variable or document-internal link: return URI unaltered
			strUri = strRef
		else:
			strUri = nodeRef.uri()
			self.addReference(nodeRef)
		return strUri
	
	def substituteOutputReference(self,strRef):
		"""Record a reference resource of this node and return the resource URI.

Since the URI is fed to new(), local paths are made relative to the current
working directory and then are made relative to this node. This makes the URI
ready for the final output content.

If strRef points to this node, it is set to the empty string.

Args:
   strRef: a string, identifying universally the referenced resource.

Returns:
   A string; the URI of the resource, modified.
"""
		try:
			nodeRef = self.new(strRef)
		except ValueError as e:
			log.warning("erroneous reference '%s' (%s)",strRef,e)
		except Warning:
			# unresolved variable or document-internal link: return URI unaltered
			pass
		else:
			if nodeRef == self:
				strRef = ""
			else:
				self.addReference(nodeRef)
				strRef = nodeRef.uri()
				try:
					strRef = urllib.parse.urlunsplit(
						urllib.parse.urlsplit(strRef)._replace(
							path=os.path.relpath(  # path of...
								nodeRef.pathOut(),    #   reference output path (might fail if not NodeLocalFile or subclass) relative to...
								self.pathOut().parent #   this node's output path parent directory
							)
						)
					)
				except AttributeError:
					pass
		return strRef
	
	def build(self,asDependency=False):
		"""Build this node.

This method is meant to be enhanced and only does the following:

   calls parent's class build() and returns False if it returns False
  
   if node is marked with MK_COPY then
      if node is needing update then
         copy file
      else
        return False
   else
      return True

If you override this method, call this implementation via super().build() and
check that it returns True before you proceed. If it returns False, you should
abord processing, since otherwise you might have run into a loop in the node
graph.

The MK_UPDATED_OUT and MK_OUTDATED_OUT marks are modified if needed.

Args:
   asDependency: a boolean; if True, the node is build as a dependency.

Returns:
   A boolean. True if the node build process should proceed, False otherwise.
"""
		# call parent's build(): this deals with touching the node, avoiding loops
		if not super().build(asDependency=asDependency):
			return False
		
		if self.hasMark(self.MK_COPY):
			if self.isNeedingUpdate():
				log.info("copying file '%s' to '%s' as requested",self.path(),self.pathOut())
				try:
					self.copyToOut()
				except (OSError,shutil.Error) as e:
					log.error("error while copying file '%s' to '%s' (%s)",self.path(),self.pathOut(),e)
				else:
					self.setMark(self.MK_UPDATED_OUT)
					self.clearMark(self.MK_OUTDATED_OUT)
					return False
			else:
				log.debug("output copy '%s' of file '%s' is already up-to-date",self.pathOut(),self.path())
				return False
		else:
			# return True to calling build() and let file-specific routine sort this out
			return True


#-------------------------------------------------------------------------------
# Node / Local / Directory
#-------------------------------------------------------------------------------


class NodeLocalDirectory(NodeLocal):
	"""Class for local directories.
"""
	def __init__(self,strPath):
		"""Constructor: initialise a local directory node.

Args:
   strPath: a string, path of the source file
"""
		super().__init__(strPath,strMime="inode/directory",strMimeOut="inode/directory")
	
	def isNeedingUpdate(self):
		"""Return True if the output file is older than the source file.

The MK_OUTDATED_OUT and MK_SKIPPED_OUT mark are modified if needed.

The class-wide BOOL_FORCED variable overrides the timestamp evaluation. If True,
this method immediately returns True.
"""
		# 1) as we are debating whether to build or not, record an output file (either processed or skipped)
		self.recordOutputFile(self.pathOut())
		# 2) assume node is outdated; set mark and return True immediately if proof is found
		self.setMark(self.MK_OUTDATED_OUT)
		# 3) forced build: return immediately
		if self.BOOL_FORCED:
			return True
		# 4) check if source is newer than output
		try:
			tOut = self.timestampOut()
			if tOut != tOut or self.timestamp() > tOut:
				return True
		except FileNotFoundError:
			# output does not exist, thus needs update
			return True
		# output is newer than source: remove outdated flag
		self.clearMark(self.MK_OUTDATED_OUT)
		self.setMark(self.MK_SKIPPED_OUT)
		return False
	
	def isNeedingUpdateDep(self):
		"""Return True if the environment data is older than the source file.

Internally isNeedingUpdate() is called; directories don't have environments.
"""
		return self.isNeedingUpdate()
	
	def build(self,asDependency=False):
		"""Build this node.

This method does the following:

   calls parent's class build() and returns False if it returns False
  
   if node is needing update then
      if node is marked with MK_COPY then
         recursively copy all files in it and the directory itself
         (if updates are needed; sort of rsync)
      else
         create directory and return True
   else
      skip directory, but record all contents as ouput files
      (so that cleanup actions won't affect them)
      
   in the end return False

If you override this method, call this implementation via super().build() and
check that it returns True before you proceed. If it returns False, you should
abord processing, since otherwise you might have run into a loop in the node
graph.

The MK_FAILED, MK_UPDATED_OUT, and MK_OUTDATED_OUT marks are modified if needed.

Args:
   asDependency: a boolean; if True, the node is build as a dependency.

Returns:
   A boolean. True if the node build process should proceed, False otherwise.
"""
		# call parent's build(): this deals with touching the node, avoiding loops
		if not super().build(asDependency=asDependency):
			return False
		
		if self.isNeedingUpdate():
			if self.hasMark(self.MK_COPY):
				# source directory is newer than output directory AND it should be copied
				#
				# instead of using shutil.copytree, iterate over all files
				# and copy individually -- and record in output file list
				# (making output dir clean-up easier)
				boolCopiedFile = False
				for pathFile in self.path().glob("**/*"):
					pathOut = self.pathOut() / pathFile.relative_to(self.path())
					try:
						boolNeedsUpdate = pathFile.stat().st_mtime < pathOut.stat().st_mtime
					except FileNotFoundError:
						boolNeedsUpdate = True
					self.recordOutputFile(pathOut)
					if boolNeedsUpdate and self.determineMarkBuild(pathOut) != self.MK_IGNORE:
						# file needs update and should not be ignored: copy
						try:
							pathOut.parent.mkdir(parents=True,exist_ok=True)
							shutil.copy2(pathFile,pathOut)
						except (OSError,shutil.Error) as e:
							log.error("error while copying file '%s' to '%s' (%s)",pathFile,pathOut,e)
							self.setMark(self.MK_FAILED)
						else:
							log.debug("copied file '%s' to '%s'",pathFile,pathOut)
							boolCopiedFile = True
					else:
						log.debug("file copy '%s' is already up-to-date",pathOut)
				# in absence of errors:
				# set marks on this node (skipped, updated) and notify user
				if not self.hasMark(self.MK_FAILED):
					if boolCopiedFile:
						self.setMark(self.MK_UPDATED_OUT)
						self.clearMark(self.MK_OUTDATED_OUT)
						log.info("copied directory '%s' recursively to '%s' as requested",self.path(),self.pathOut())
					else:
						log.debug("directory copy '%s' is already up-to-date",self.pathOut())
			else:
				# normal node operation: create dir if needed
				try:
					self.pathOut().mkdir(parents=True,exist_ok=True)
				except OSError as e:
					self.error("could not create directory '%s'", self.pathOut())
					self.setMark(self.MK_FAILED)
				else:
					log.info("created directory '%s'",self.pathOut())
					self.setMark(self.MK_UPDATED_OUT)
					self.clearMark(self.MK_OUTDATED_OUT)
					return True
		else:
			# skip directory, but record all contents as output files
			for pathFile in self.path().glob("**/*"):
				self.recordOutputFile(self.pathOut() / pathFile.relative_to(self.path()))
			log.debug("directory '%s' is already up-to-date",self.pathOut())
		
		return False


#-------------------------------------------------------------------------------
# Node / Local / File / Markdown
#-------------------------------------------------------------------------------


class NodeLocalFileMarkdown(NodeLocalFile):
	"""Class for local Markdown files.
"""
	MARKDOWN = md.Markdown()
	
	RE_VAR_HTML_CONTENT = re.compile(r'''\$htmlContent|\${htmlContent}''',flags=re.IGNORECASE)
	RE_VAR_SIMPLE = re.compile(r'''[^\$]\$([a-zA-Z0-9_-]+)''',flags=re.IGNORECASE)
	RE_VAR_CURLY = re.compile(r'''\${([a-zA-Z0-9_-]+)}''',flags=re.IGNORECASE)
	
	def __init__(self,strPath,strCharset):
		"""Constructor: initialise a Markdown file node.

Args:
   strPath: a string, path of the source file.
   strCharset: a string defining the charset to be used when reading the file.
"""
		super().__init__(strPath,strMime="text/markdown",strMimeOut="text/html",strCharset=strCharset)
	
	def pathOut(self):
		"""Return the output file path as pathlib.Path instance.
"""
		return super().pathOut().with_suffix(".html")
	
	def build(self,asDependency=False):
		"""Build this node.

This method does the following:

   calls parent's class build() and returns False if it returns False
  
   if node is needing dependency update then
      read source file
      convert markdown to html, apply recordReference() to all href/src
      import metadata
      store content, title, and toc in environment
      update environment timestamp
   
   if as dependency then
      return True
   
   if node is needing output update then
      build all dependencies
      load content from environment
      apply template if defined (load template, apply htmlContent variable)
      replace all variables, load content if needed (html*, svg*, css*)
      replace all $$ with $
      process generated html, apply substituteOutputReference() to all href/src
      write output file
   
   build all references
   in the end return False since there is nothing more to do

If you override this method, call this implementation via super().build() and
check that it returns True before you proceed. If it returns False, you should
abord processing, since otherwise you might have run into a loop in the node
graph.

The MK_UPDATED_DEP, MK_UPDATED_OUT, MK_OUTDATED_DEP, and MK_OUTDATED_OUT marks
are modified if needed.

Args:
   asDependency: a boolean; if True, the node is build as a dependency.

Returns:
   A boolean. True if the node build process should proceed, False otherwise.
   As a top-level build method, its return value is unlikely to be processed.
"""
		# call parent's build(): this deals with touching the node, avoiding loops
		if not super().build(asDependency):
			return False
		
		if self.isNeedingUpdateDep():
			# timestamp of source file is newer than timestamp of corresponding environment
			#
			# convert from markdown to HTML
			strContent,dctMeta,strToc,strTitle = self.MARKDOWN.convert(
				strMdSource=self.pathRead(),
				funProcessReference=self.recordReference
			)
			# clean up strToc (might contain only empty tag)
			strToc = html5.processFragment(strToc,doRemoveEmptyTags=self.DO_REMOVE_EMPTY_TAGS)
			# register reference strings and replace all strings with the normalised Node URI
			#strContent = self.recordReferences(setStrRef,strContent)
			# import Metadata: type conversion, dependency node creation/recording
			self.importMetadata(dctMeta,strPathReference=self.path().parent)
			# update environment: set HTML content and ToC content; update timestamp to source file's timestamp
			self.setVariable("htmlContent",strContent)
			self.setVariable("htmlToc",strToc)
			self.setVariable("titleContent",strTitle)
			self.setTimestampEnvironment()
			log.info("updated dependency data of file '%s'",self.uri())
		else:
			log.debug("dependency data of file '%s' is already up-to-date",self.uri())
		
		if asDependency:
			# dependency processing stops here
			return True
		
		# processing of final data (collect deps, apply template, apply variables, parse HTML)
		if self.isNeedingUpdate():
			# build all dependencies
			for nodeDep in self.iterateDependencies():
				nodeDep.build(asDependency=True)
			# apply template if needed
			try:
				# substitute all occurrences of $htmlContent with this file's content
				# and define the result as the new content
				nodeTemplate = self.getVariable("pathTemplate")
				self.addDependency(nodeTemplate)
				nodeTemplate.build(asDependency=True)
				strContent = self.RE_VAR_HTML_CONTENT.sub(
					self.getVariable("htmlContent"),
					nodeTemplate.getVariable("htmlContent")
				)
			except KeyError:
				# no template or content found: just use this file's content
				strContent = self.getVariable("htmlContent")
			
			# replace all $$ with $\x03 to mask all escaped dollar signs
			strContent = strContent.replace("$$","$\x03")
			
			# collect all variables in the code, auto-generate missing data and replace variables with data
			datetimeSource = datetime.datetime.fromtimestamp(self.timestamp(),tz=datetime.timezone.utc).astimezone(self.getVariable("timezone"))
			for strKey in set(self.RE_VAR_SIMPLE.findall(strContent) + self.RE_VAR_CURLY.findall(strContent)):
				strKey = strKey.lower()
				try:
					# look-up key in node's environment
					strValue = self.getVariable(strKey)
				except KeyError:
					# variable does not exist; does it need to be generated?
					# default value of unknown variables is the original variable reference,
					# so that the following code can fall-through and strValue is always defined 
					strValue = "$" + strKey
					
					if strKey[0:4] == "date" and strKey[4:10] != "format":
						# the current document's date is requested
						#  - get date format with same suffix
						#  - call strftime() for given format
						#  - no need to store in environment (transient data)
						try:
							strValue = datetimeSource.strftime(self.getVariable("dateformat" + strKey[4:]))
						except KeyError:
							log.warning("file '%s' requests variable %s, but required date format '%s' is not defined",self.uri(),strKey,"dateformat"+strKey[4:])
					
					elif strKey.startswith(("html","svg","css")) and strKey != "htmlContent" and strKey != "htmlToc":
						# dependency file content requested; look for corresponding path variable
						if strKey[0:4] == "html":
							prefix = "html"
							suffix = strKey[4:]
						else:
							prefix = strKey[0:3]
							suffix = strKey[3:]
						try:
							nodeContent = self.getVariable("path" + suffix)
						except KeyError:
							log.warning("file '%s' requests variable %s, but it is neither defined explicitly nor implied by %s",self.uri(),strKey,"path"+suffix)
						else:
							self.addDependency(nodeContent)
							# found corresponding path: extract file content
							if prefix == "html" and isinstance(nodeContent,(NodeLocalFileMarkdown,NodeLocalFileHtml)):
								try:
									strValue = nodeContent.getVariable("htmlContent")
								except KeyError:
									log.warning("file '%s', requested by variable %s, has no content",nodeContent.uri(),strKey)
							elif prefix == "svg" and isinstance(nodeContent,NodeLocalFileSvg):
								try:
									strValue = nodeContent.getVariable("svgContent")
								except KeyError:
									log.warning("file '%s', requested by variable %s, has no content",nodeContent.uri(),strKey)
								pass
							elif prefix == "css" and isinstance(nodeContent,NodeLocalFileCss):
								try:
									strValue = nodeContent.getVariable("cssContent")
								except KeyError:
									log.warning("file '%s', requested by variable %s, has no content",nodeContent.uri(),strKey)
							else:
								if prefix == "html":
									prefix = "html|markdown"
								log.warning("file '%s', requested by variable %s, has an unsupported format (not %s)",nodeContent.uri(),strKey,prefix)
					
					elif strKey[0:5] == "title" and strKey != "titletoc" and strKey != "titlecontent":
						# title requested which was not yet defined
						# look for any path* variable leading to html/markdown content
						prefix = "title"
						suffix = strKey[5:]
						try:
							nodeContent = self.getVariable("path" + suffix)
						except KeyError:
							log.warning("file '%s' requests variable %s, but it is neither defined explicitly nor implied by %s",self.uri(),strKey,"path"+suffix)
						else:
							self.addDependency(nodeContent)
							# found corresponding path: extract file content
							try:
								strValue = nodeContent.getVariable("titleContent")
							except KeyError:
								log.warning("file '%s', requested by variable %s, has no title",nodeContent.uri(),strKey)
				
				# value post-processing
				if isinstance(strValue,Node):
					# translate Node or subclass instance values to URI strings and
					# record the path node as reference
					strValue = strValue.uri()
				elif (strKey == "titletoc" or strKey == "htmltoc") and (not self.getVariable("createtoc") or not self.getVariable("htmlToc")):
					# suppress printing of table of contents title if no toc is needed or toc is empty
					strValue = ""
				
				# finally substitute the variable reference with its value
				strContent = re.sub(f'\${strKey}|\${{{strKey}}}',str(strValue),strContent,flags=re.IGNORECASE)
			
			# after having expanded all variables names: replace masked dollar signs
			strContent = strContent.replace("$\x03","$")
			
			# let html5lib parse strContent and collect any references (href,src)
			strContentHtml,strTitle = html5.parseString(
				strContent=strContent,
				strEncoding=self.CHARSET_DEFAULT,
				doRemoveEmptyTags=self.DO_REMOVE_EMPTY_TAGS,
				funProcessReference=self.substituteOutputReference
			)
			
			# in the end, write to output file
			self.pathOutWrite(strContentHtml)
			log.info("updated output file '%s'",self.pathOut())
			
		else:
			log.debug("output file '%s' is already up-to-date",self.pathOut())
		
		# in any case: build all references
		for nodeRef in self.iterateReferences():
			nodeRef.build(asDependency=False)
		
		return False


#-------------------------------------------------------------------------------
# Node / Local / File / HTML
#-------------------------------------------------------------------------------


class NodeLocalFileHtml(NodeLocalFile):
	"""Class for local Hyper-Text Markup Language files.
"""
	def __init__(self,strPath,strCharset):
		"""Constructor: initialise a HTML file node.

Args:
   strPath: a string, path of the source file.
   strCharset: a string defining the charset to be used when reading the file.
"""
		super().__init__(strPath,strMime="text/html",strMimeOut="text/html",strCharset=strCharset)
	
	def build(self,asDependency=False):
		"""Build this node.

This method does the following:

   calls parent's class build() and returns False if it returns False
  
   if node is needing dependency update then
      read source file
      process html, apply recordReference() to all href/src
      store content and title in environment
      update environment timestamp
   
   if as dependency then
      return True
   
   if node is needing output update then
      read content from environment
      process html, apply substituteOutputReference() to all href/src
      write output file
   
   build all references
   in the end return False since there is nothing more to do

If you override this method, call this implementation via super().build() and
check that it returns True before you proceed. If it returns False, you should
abord processing, since otherwise you might have run into a loop in the node
graph.

The MK_UPDATED_DEP, MK_UPDATED_OUT, MK_OUTDATED_DEP, and MK_OUTDATED_OUT marks
are modified if needed.

Args:
   asDependency: a boolean; if True, the node is build as a dependency.

Returns:
   A boolean. True if the node build process should proceed, False otherwise.
   As a top-level build method, its return value is unlikely to be processed.
"""
		# call parent's build(): this deals with touching the node, avoiding loops
		if not super().build(asDependency):
			return False
		
		if self.isNeedingUpdateDep():
			# timestamp of source file is newer than timestamp of environment
			#
			# let html5lib parse strContent and collect any references (href,src)
			strContent,strTitle = html5.parseString(
				strContent=self.pathRead(),
				strEncoding=self.CHARSET_DEFAULT,
				doRemoveEmptyTags=self.DO_REMOVE_EMPTY_TAGS,
				funProcessReference=self.recordReference
			)
			# setup HTML environment
			self.setVariable("htmlContent",strContent)
			self.setVariable("titleContent",strTitle)
			self.setTimestampEnvironment()
			log.info("updated dependency data of file '%s'",self.uri())
		else:
			log.debug("dependency data of file '%s' is already up-to-date",self.uri())
		
		if asDependency:
			# dependency processing stops here
			return True
		
		if self.isNeedingUpdate():
			# correct references: make local references relative to this node
			strContent,strTitle = html5.parseString(
				strContent=self.getVariable("htmlContent"),
				strEncoding=self.CHARSET_DEFAULT,
				doRemoveEmptyTags=self.DO_REMOVE_EMPTY_TAGS,
				funProcessReference=self.substituteOutputReference
			)
			# write to output file
			self.pathOutWrite(strContent)
			log.info("updated output file '%s'",self.pathOut())
			
		else:
			log.debug("output file '%s' is already up-to-date",self.pathOut())
		
		# in any case: build all references
		for nodeRef in self.iterateReferences():
			nodeRef.build(asDependency=False)
		
		return False



#-------------------------------------------------------------------------------
# Node / Local / File / SVG
#-------------------------------------------------------------------------------


class NodeLocalFileSvg(NodeLocalFile):
	"""Class for local Scalable Vector Graphics files.
"""
	def __init__(self,strPath,strCharset):
		"""Constructor: initialise an SVG file node.

Args:
   strPath: a string, path of the source file.
   strCharset: a string defining the charset to be used when reading the file.
"""
		super().__init__(strPath,strMime="image/svg+xml",strMimeOut="image/svg+xml",strCharset=strCharset)
	
	def build(self,asDependency=False):
		"""Build this node.

This method does the following:

   calls parent's class build() and returns False if it returns False
  
   if node is needing dependency update then
      read source file
      process svg-xml, apply recordReference() to all xlink:href/src
      store content in environment
      update environment timestamp
   
   if as dependency then
      return True
   
   if node is needing output update then
      read content from environment
      process svg-xml, apply substituteOutputReference() to all xlink:href/src
      write output file
   
   build all references
   in the end return False since there is nothing more to do

If you override this method, call this implementation via super().build() and
check that it returns True before you proceed. If it returns False, you should
abord processing, since otherwise you might have run into a loop in the node
graph.

The MK_UPDATED_DEP, MK_UPDATED_OUT, MK_OUTDATED_DEP, and MK_OUTDATED_OUT marks
are modified if needed.

Args:
   asDependency: a boolean; if True, the node is build as a dependency.

Returns:
   A boolean. True if the node build process should proceed, False otherwise.
   As a top-level build method, its return value is unlikely to be processed.
"""
		# call parent's build(): this deals with touching the node, avoiding loops
		if not super().build(asDependency):
			return False
		
		if self.isNeedingUpdateDep():
			# timestamp of source file is newer than timestamp of environment
			#
			strContent = svg.parse(
				self.path(),
				self.recordReference
			)
			# setup SVG environment
			self.setVariable("svgContent",strContent)
			self.setTimestampEnvironment()
			log.info("updated dependency data of file '%s'",self.uri())
		else:
			log.debug("dependency data of file '%s' is already up-to-date",self.uri())
		
		if asDependency:
			# dependency processing stops here
			return True
		
		if self.isNeedingUpdate():
			# correct references: make local references relative to this node
			strContent = svg.parseString(
				self.getVariable("svgContent"),
				self.substituteOutputReference
			)
			# write to output file
			self.pathOutWrite(strContent)
			log.info("updated output file '%s'",self.pathOut())
			
		else:
			log.debug("output file '%s' is already up-to-date",self.pathOut())
		
		# in any case: build all references
		for nodeRef in self.iterateReferences():
			nodeRef.build(asDependency=False)
		
		return False


#-------------------------------------------------------------------------------
# Node / Local / File / CSS
#-------------------------------------------------------------------------------


class NodeLocalFileCss(NodeLocalFile):
	"""Class for local Cascading Stylesheets files.
"""
	def __init__(self,strPath,strCharset):
		"""Constructor: initialise a CSS file node.

Args:
   strPath: a string, path of the source file.
   strCharset: a string defining the charset to be used when reading the file.
"""
		super().__init__(strPath,strMime="text/css",strMimeOut="text/css",strCharset=strCharset)

	def build(self,asDependency=False):
		"""Build this node.

This method does the following:

   calls parent's class build() and returns False if it returns False
  
   if node is needing dependency update then
      read source file
      process css, apply recordReference() to all @import/url()
      store content in environment
      update environment timestamp
   
   if as dependency then
      return True
   
   if node is needing output update then
      read content from environment
      process css, apply substituteOutputReference() to all @import/url()
      write output file
   
   build all references
   in the end return False since there is nothing more to do

If you override this method, call this implementation via super().build() and
check that it returns True before you proceed. If it returns False, you should
abord processing, since otherwise you might have run into a loop in the node
graph.

The MK_UPDATED_DEP, MK_UPDATED_OUT, MK_OUTDATED_DEP, and MK_OUTDATED_OUT marks
are modified if needed.

Args:
   asDependency: a boolean; if True, the node is build as a dependency.

Returns:
   A boolean. True if the node build process should proceed, False otherwise.
   As a top-level build method, its return value is unlikely to be processed.
"""
		# call parent's build(): this deals with touching the node, avoiding loops
		if not super().build(asDependency):
			return False
		
		if self.isNeedingUpdateDep():
			# timestamp of source file is newer than timestamp of environment
			#
			# read file and strip comments (to eliminate commented-out url()/src())
			strContent = css.parse(self.pathRead(),self.recordReference)
			# setup CSS environment
			self.setVariable("cssContent",strContent)
			self.setTimestampEnvironment()
			log.info("updated dependency data of file '%s'",self.uri())
		else:
			log.debug("dependency data of file '%s' is already up-to-date",self.uri())
		
		if asDependency:
			# dependency processing stops here
			return True
		
		if self.isNeedingUpdate():
			# correct references: make local references relative to this node
			strContent = css.parse(self.getVariable("cssContent"),self.substituteOutputReference)
			# write to output file
			self.pathOutWrite(strContent)
			log.info("updated output file '%s'",self.pathOut())
		else:
			log.debug("output file '%s' is already up-to-date",self.pathOut())
		
		# in any case: build all references
		for nodeRef in self.iterateReferences():
			nodeRef.build(asDependency=False)
		
		return False


#-------------------------------------------------------------------------------
# Node / Local / File / Miscellaneous
#-------------------------------------------------------------------------------


class NodeLocalFileMisc(NodeLocalFile):
	"""Class for local miscellaneous files.
"""
	def __init__(self,strPath,strMime,strCharset):
		"""Constructor: initialise a miscellaneous file node.

Args:
   strPath: a string, path of the source file.
   strMime: a string, MIME type of the source file.
   strCharset: a string defining the charset to be used when reading the file.
"""
		super().__init__(strPath,strMime=strMime,strMimeOut=strMime,strCharset=strCharset)
	
	def build(self,asDependency=False):
		"""Build this node.

This method does the following:

   calls parent's class build() and returns False if it returns False
  
   if node is needing update then
      copy source file to output
   
   in the end return False since there is nothing more to do

Args:
   asDependency: a boolean; if True, the node is build as a dependency.

Returns:
   A boolean. True if the node build process should proceed, False otherwise.
   As a top-level build method, its return value is unlikely to be processed.
"""
		# call parent's build(): this deals with touching the node, avoiding loops
		if not super().build(asDependency):
			return False
		if self.isNeedingUpdate():
			self.copyToOut()
			log.info("updated output file '%s'",self.pathOut())
		else:
			log.debug("output file '%s' is already up-to-date",self.pathOut())
		return False


#-------------------------------------------------------------------------------
# Node / Local / File / Unknown
#-------------------------------------------------------------------------------


class NodeLocalFileUnkown(NodeLocalFile):
	"""Class for local unknown (not-yet-existing) files.
"""
	def __init__(self,strPath):
		"""Constructor: initialise an unknown file node.

Args:
   strPath: a string, path of the source file.
"""
		super().__init__(strPath,strMime="inode/unknown",strMimeOut="inode/unknown",strCharset="utf-8")
	
	def build(self,asDependency=False):
		"""Build this node.

As the file does not exist, does noting and returns always False.
"""
		return False


#-------------------------------------------------------------------------------
# Remote resources classes
#-------------------------------------------------------------------------------


class NodeRemote(Node):
	"""Abstract class for remote resources.
"""
	def __init__(self,strUri):
		"""Constructor: initialise an abstract remote resource.

Also sets the MK_IGNORE mark.

Args:
   strUri: a string universally identifying the resource.
"""
		super().__init__(strUri)
		self.setMark(self.MK_IGNORE)


class NodeRemoteMailto(NodeRemote):
	"""Class for remote Mailto resources.
"""
	pass


class NodeRemoteHttp(NodeRemote):
	"""Class for remote HTTP/HTTPS resources.
"""
	pass


class NodeRemoteMisc(NodeRemote):
	"""Class for remote miscellaneous resources.
"""
	pass


#-------------------------------------------------------------------------------
# Helper functions
#-------------------------------------------------------------------------------

# generate a mapping of class names to classes
DCT_NAME_TO_CLASS = dict(inspect.getmembers(sys.modules[__name__], lambda member: inspect.isclass(member) and member.__module__ == __name__))
DCT_CLASS_TO_NAME = {cls:name for name,cls in DCT_NAME_TO_CLASS.items()}


def getClassHierarchy(mainclass):
	"""Return an ASCII art representation of the class structure.

Args:
   mainclass: a class; origin of the class hierarchy graph.

Returns:
   A list of strings; join the list items with newlines to get a multiline text.
"""
	lstNameSubclasses = [mainclass.__name__]
	lstSubclasses = mainclass.__subclasses__()
	while lstSubclasses:
		subclass = lstSubclasses.pop(0)
		lstNameSub = getClassHierarchy(subclass)
		while lstNameSub:
			name = lstNameSub.pop(0)
			if name.startswith((" +"," `"," |","  ")):
				if lstSubclasses:
					prefix = " |   "
				else:
					prefix = "     "
			else:
				if lstSubclasses:
					prefix = " +-- "
				else:
					prefix = " `-- "
			lstNameSubclasses.append(f'{prefix}{name}')
	return lstNameSubclasses


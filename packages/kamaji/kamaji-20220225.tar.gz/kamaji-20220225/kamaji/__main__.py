#!/usr/bin/env python3
"""Kamaji Static Website Generator: Main application module
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
import argparse # parse commandline arguments
import sys      # terminate with error using sys.exit()
import pathlib  # file path management
import zoneinfo # set the default timezone "UTC"
import importlib.resources # access to the app's file resources
import re

# import own modules
from . import nodes     # Node management module
from . import log       # custom logging module
from . import resources # example/doc files
from . import bashmd    # colourful BASh markdown renderer

KAMAJI_NAME = "kamaji"
KAMAJI_VERSION = "20220225"
KAMAJI_NAME_FULL = f"{KAMAJI_NAME} v{KAMAJI_VERSION}"
KAMAJI_SITE = "https://code.abelbeck.info/projects/kamaji.html"

KAMAJI_PATH_OUT = ".kamaji/out"
KAMAJI_PATH_DB  = ".kamaji/nodes.json"

DCT_DEFAULT_VALUES = {
	"kamajiName"    : KAMAJI_NAME,
	"kamajiVersion" : KAMAJI_VERSION,
	"kamajiNameFull": KAMAJI_NAME_FULL,
	"kamajiSite"    : KAMAJI_SITE,
	"language"      : "en",
	"timezone"      : zoneinfo.ZoneInfo("UTC"),
	"dateFormatISO" : "%Y-%m-%dT%H:%M:%S%z",
	"createToc"     : False,
	"titleToc"      : "On this page",
}

def main():
	"""Main Kamaji function: parse commandline arguments, execute requested sub-command.
"""
	#
	# Set-up the commandline argument parser
	#
	parser = argparse.ArgumentParser(description="Manage a static website.")
	parser.add_argument("-l","--loglevel",
		help="Set the minimum log level (default: info)",
		choices=("debug","info","warn","err","crit"),
		default="info"
	)
	parser.add_argument("--version",
		action="version",
		version=KAMAJI_NAME_FULL
	)
	
	subparsers = parser.add_subparsers(dest="subparserName",required=True)
	
	parser_demo = subparsers.add_parser("demo",
		help="Initialise an example source directory",
		description="Populate the current directory with some example files."
	)
	
	parser_build = subparsers.add_parser("build",
		help="Build a static website",
		formatter_class=argparse.RawTextHelpFormatter,
		description="Build a static website in the current directory.",
		epilog=f"""Default values:
   PATHOUT = {KAMAJI_PATH_OUT}
   PATHDB  = {KAMAJI_PATH_DB}

The options --exclude, --include, and --copy accept patterns with the following special characters:
  '*'      matches everything
  '**'     matches everything in the current and all subdirectories, recursively
  '?'      matches any single character
  '[seq]'  matches any character in seq
  '[!seq]' matches any character not in seq

Output directory PATHOUT and node database file PATHDB are ignored automatically.

The options --ignore and --copy may be specified multiple times.
"""
	)
	parser_build.add_argument("--no-prune",
		help="do not remove empty HTML tags from the final output",
		action="store_true"
	)
	parser_build.add_argument("--no-clean",
		help="do not remove stale files from the output directory",
		action="store_true"
	)
	parser_build.add_argument("--force",
		help="force rebuilding by ignoring any existing node DB",
		action="store_true"
	)
	parser_build.add_argument("--exclude",
		help="exclude any file matching PATTEXC",
		metavar="PATTEXC",
		action="append",
		default=[]
	)
	parser_build.add_argument("--include",
		help="include any file matching PATTINC",
		metavar="PATTINC",
		action="append",
		default=[]
	)
	parser_build.add_argument("--copy",
		help="instead of processing, just copy any file matching PATTCPY",
		metavar="PATTCPY",
		action="append",
		default=[]
	)
	parser_build.add_argument("--output",
		help="define the path PATHOUT of the output directory",
		metavar="PATHOUT",
		default=KAMAJI_PATH_OUT
	)
	parser_build.add_argument("--db",
		help="define the path PATHDB of the node JSON database",
		metavar="PATHDB",
		default=KAMAJI_PATH_DB
	)
	
	parser_map = subparsers.add_parser("map",
		help="Create a graph of the site structure",
		formatter_class=argparse.RawTextHelpFormatter,
		description=f"""Create a graph of the node structure in the current directory.""",
		epilog=f"""Default values:
   PATHDB = {KAMAJI_PATH_DB}
   FORMAT = svg
   ENGINE = dot

Available node classes (option --class):
{chr(10).join(["   "+i for i in nodes.getClassHierarchy(nodes.Node)])}

Any local link is made relative to the output file's directory.

Option --all equals "--class Node --deps --refs" and takes precedence over --site.

Option --site equals "--class NodeLocalFileMarkdown --class NodeLocalFileHtml --class NodeLocalDirectory --refs" and takes precedence over --class.

Option --attribute allows attribute definition for nodes and edges.
If CLS equals "graph", this defines a graph attribute.
If CLS equals "nodes", this defines a general node attribute.
If CLS equals "edges", "dep", or "ref", this defines a general, dependency, or reference edge attribute.
Otherwise CLS is interpreted as node class name (see above) and defines the attribute for that node class and all subclasses.

The options --exclude and --include accept a pattern with the following special characters:
  '*'      matches everything
  '**'     matches everything in the current and all subdirectories, recursively
  '?'      matches any single character
  '[seq]'  matches any character in seq
  '[!seq]' matches any character not in seq

If --undirected is passed, Kamaji will create an undirected graph. Otherwise dependency edges point from the dependency towards the dependent node, and reference edges point from the referrer to the referenced node.

The option --merge lets Kamaji merge parallel edges (i.e. pairwise reference/dependency).

Extra class "edgedep" and "edgeref" are added to dependency and reference edges, respectively. This is useful when styling SVG output over CSS.

The options --class, --attribute, --exclude, and --include may be specified multiple times.
"""
	)
	parser_map.add_argument("PATHOUT",
		help="define the path PATHOUT of the sitemap output file. Suffixes are appended as needed.",
	)
	parser_map.add_argument("--db",
		help=f"define the path PATHDB of the node JSON database [default: {KAMAJI_PATH_DB}]",
		metavar="PATHDB",
		default=KAMAJI_PATH_DB
	)
	parser_map.add_argument("--format",
		help="define the output format FORMAT of the sitemap output file",
		default="svg",
		dest="fmt"
		
	)
	parser_map.add_argument("--engine",
		help="define the layout engine ENGINGE used by GraphViz",
		default="dot",
	)
	parser_map.add_argument("--exclude",
		help="exclude any file matching PATTEXC",
		metavar="PATTEXC",
		action="append",
		default=[]
	)
	parser_map.add_argument("--include",
		help="include any file matching PATTINC",
		metavar="PATTINC",
		action="append",
		default=[]
	)
	parser_map.add_argument("--class",
		help="""include all nodes of given class and its subclasses""",
		action="append",
		default=[],
		dest="cls"
	)
	parser_map.add_argument("--deps",
		help="include all nodes that are dependencies of others",
		action="store_true"
	)
	parser_map.add_argument("--refs",
		help="include all nodes that are references to others",
		action="store_true"
	)
	parser_map.add_argument("--all",
		help="include nodes of all classes and all relationships",
		action="store_true"
	)
	parser_map.add_argument("--site",
		help="include all website nodes, suitable for a sitemap",
		action="store_true"
	)
	parser_map.add_argument("--attribute",
		help="define an additional attribute KEY=VAL for a given class CLS",
		metavar=("CLS","KEY","VAL"),
		nargs=3,
		action="append",
		default=[],
		dest="attr"
	)
	parser_map.add_argument("--undirected",
		help="create an undirected graph",
		action="store_true"
	)
	parser_map.add_argument("--merge",
		help="merge parallel edges (i.e. use edge concentrators)",
		action="store_true"
	)
	
	parser_info= subparsers.add_parser("info",
		help="show documentation on Kamaji",
		description="Show documentation on Kamaji."
	)
	parser_info.add_argument("--raw",
		help="show documentation in raw markdown format",
		action="store_true"
	)
	
	parser_license = subparsers.add_parser("license",
		help="show Kamaji's license text",
		description="Show Kamaji's license text."
	)
	parser_license.add_argument("--raw",
		help="show license in raw markdown format",
		action="store_true"
	)
	
	args = parser.parse_args()
	log.setLevel(args.loglevel)
	log.debug(f"commandline-arguments:\n{chr(10).join([f'   --{argname} = {argvalue!r}' for argname,argvalue in args.__dict__.items()])}")
	
	#
	# process subcommands
	#
	if args.subparserName == "build":
		#
		# Build the documents in the current directory
		#
		# process commandline arguments
		pathDirOutput = pathlib.Path(args.output)
		try:
			nodes.Node.setPathDirOut(pathDirOutput)
		except FileExistsError:
			log.critical("Output directory path '%s' points to an existing file.",pathDirOutput)
		
		nodes.NodeLocalFile.setEmptyTagRemoval(not args.no_prune)
		nodes.Node.setPathsExclude(*args.exclude,pathDirOutput,args.db)
		nodes.Node.setPathsInclude(*args.include)
		nodes.Node.setPathsCopy(*args.copy)
		nodes.Node.setForced(args.force)
		
		# define default environment values
		for key,value in DCT_DEFAULT_VALUES.items():
			nodes.NodeLocalFile.setDefaultVariable(key,value)
		
		if not args.force:
			try:
				nodes.Node.load(args.db)
			except IsADirectoryError:
				log.critical("Invalid node database path specified (found a directory. expected a file). Exiting.")
				sys.exit(2)
			except FileNotFoundError:
				log.info("Node database file not found, starting with a fresh one.")
			except PermissionError:
				log.critical("Node database file not accessible. Exiting.")
				sys.exit(2)
			except ValueError as e:
				log.error("%s",e)
				log.info("Starting with a fresh node database.")
			else:
				log.info("Node database loaded.")
		else:
			log.info("Forced building, ignoring any node database.")
		
		# create first node for file "index.md" and build it
		try:
			nodeIndex = nodes.Node.new("index.md")
		except ValueError as e:
			log.critical("There is no 'index.md' in the current directory. Nothing to build.")
			log.critical(e)
		else:
			try:
				nodeIndex.build()
			except ValueError as e:
				log.critical("Ran into an exception while building: %s",e)
		
		# safe node database
		try:
			nodes.Node.dump(args.db)
		except ValueError as e:
			log.error("%s",e)
		
		# copy all files matched by all args.copy patterns
		nodes.Node.copyAllCopyPaths()
		
		if not args.no_clean:
			# clean up output directory (remove stale files) by comparing the list
			# of all files in the output directory with the NodeLocal class-internal
			# list of written files; remove all files not in the set of written files
			setFiles = set()
			for pathFile in pathDirOutput.glob("**/*"):
				if not nodes.NodeLocal.isInOutputFileSet(pathFile):
					setFiles.add(pathFile)
			# now setFiles contains the following files:
			#  - files and directories not created by the last build run
			#  - directories that were implicitly created
			# iterate over set, remove files, remove dirs if empty
			for pathFile in setFiles:
				try:
					pathFile.unlink()
					log.info("deleted stale file '%s'",pathFile)
				except IsADirectoryError:
					try:
						pathFile.rmdir()
						log.info("deleted stale directory '%s'",pathFile)
					except OSError:
						pass
		
		# print some statistics and
		# exit with 2 (errors and criticals) or 0 (success, or only warnings)
		stats = nodes.Node.getStatistics()
		if any(stats):
			for strAction,numAction in {"updated":stats[0],"skipped":stats[1],"failed":stats[2]}.items():
				if numAction == 1:
					log.info("One node %s.",strAction)
				elif numAction > 1:
					log.info("%d nodes %s.",numAction,strAction)
		else:
			log.info("Nothing to do, all's well.")
		
		numWarnings = log.getNumWarnings()
		if numWarnings == 1:
			log.info("One warning received.")
		elif numWarnings > 1:
			log.info("%d warnings received.",numWarnings)
		numErrors = log.getNumErrors()
		if numErrors == 1:
			log.info("One error encountered.")
		elif numErrors > 1:
			log.info("%d errors encountered.",numErrors)
		numCritical = log.getNumCritical()
		if numCritical == 1:
			log.info("Got into one critical situation.")
		elif numCritical > 1:
			log.info("Got into %d critical situations.",numCritical)
		if numErrors or numCritical:
			sys.exit(2)
		else:
			sys.exit(0)
	
	elif args.subparserName == "map":
		#
		# create a graph of the node structure
		#
		# first load a node structure from a given JSON node database.
		try:
			nodes.Node.load(args.db)
		except IsADirectoryError:
			log.critical("Invalid node database path specified (found a directory. expected a file).")
			sys.exit(2)
		except FileNotFoundError:
			log.info("Node database file not found.")
			sys.exit(2)
		except PermissionError:
			log.critical("Node database file not accessible.")
			sys.exit(2)
		except ValueError as e:
			log.critical("%s",e)
			sys.exit(2)
		
		if args.all:
			setClasses = set(("Node",))
			boolDeps = True
			boolRefs = True
		elif args.site:
			setClasses = set(("NodeLocalFileMarkdown","NodeLocalFileHtml","NodeLocalDirectory"))
			boolDeps = False
			boolRefs = True
		else:
			setClasses = set(args.cls)
			boolDeps = args.deps
			boolRefs = args.refs
		
		dctAttr = {}
		for cls,key,value in args.attr:
			try:
				dctAttr[cls][key] = value
			except KeyError:
				dctAttr[cls] = { key:value }
		
		try:
			strFileOut = nodes.Node.renderMap(
				pathOut = args.PATHOUT,
				boolDeps = boolDeps,
				boolRefs = boolRefs,
				boolUndirected = args.undirected,
				boolMerge = args.merge,
				dctAttr = dctAttr,
				setClasses = setClasses,
				setExclude = set(args.exclude),
				setInclude = set(args.include),
				strFormat = args.fmt,
				strEngine = args.engine
			)
		except ValueError as e:
			log.critical("Ran into an exception while mapping: %s",e)
			sys.exit(2)
		else:
			log.info("Created file '%s'",strFileOut)
	
	elif args.subparserName == "info":
		#
		# print information on the Kamaji system
		#
		strContentRaw = importlib.resources.read_text(resources,"index.md")
		for key,value in DCT_DEFAULT_VALUES.items():
			strContentRaw = re.sub(f'\${key}',str(value),strContentRaw,flags=re.IGNORECASE)
		strContentRaw = strContentRaw.replace("$$","$")
		if args.raw:
			print(strContentRaw)
		else:
			print(bashmd.BashMarkdownParser().parse(strContentRaw))
	
	elif args.subparserName == "license":
		#
		# print information on the Kamaji system
		#
		strContentRaw = importlib.resources.read_text(resources,"license.md").replace("$$","$")
		if args.raw:
			print(strContentRaw)
		else:
			print(bashmd.BashMarkdownParser().parse(strContentRaw))
	
	elif args.subparserName == "demo":
		#
		# populate current directory with the demo files from resource
		#
		for strName in ("favicon.svg","index.md","license.md","main.css","main.js","menu.md","howto.md","template.html"):
			bytesContent = importlib.resources.read_binary(resources,strName)
			try:
				with open(strName,"wb") as f:
					f.write(bytesContent)
			except Exception as e:
				log.error("failed to create file '%s' (%s)",strName,e)
			else:
				log.info("created file '%s'",strName)
		log.info("""You will need a special CSS file for syntax highlighting. You can generate it with
the following command (in this example as file code.css):

	pygmentize -S STYLE -f html -a .codehilite > code.css

STYLE is a pre-defined style of Pygments. You can obtain an overview of
supported styles with the following command:
	
	pygmentize -L style

Afterwards you can import that file by uncommenting the @import in main.css.

Kamaji's demo theme plays well with the solarized-dark style:

	pygmentize -S solarized-dark -f html -a .codehilite > code.css""")



if __name__ == "__main__":
	main()

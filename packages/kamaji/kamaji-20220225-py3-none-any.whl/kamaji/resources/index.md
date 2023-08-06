---
authorName: Kamaji
authorMail: Kamaji@abelbeck.info
pathStylesheet: main.css
pathScript: main.js
pathIcon: favicon.svg
pathTemplate: template.html
pathNav: menu.md
createToc: yes
---

# Kamaji Static Website Generator

Copyright (C) 2021-2022 Frank Abelbeck <kamaji@abelbeck.info>

Version: $kamajiversion

License: GLP 3

## Overview

Kamaji is a static website generator. It generates HTML files from Markdown
source files, processing their metadata and following all local file references.

Kamaji will only process source files that are newer than the output. It will
build all dependencies or references as it goes along.

Metadata in a Markdown file defines the environment of that file. You configure
your entire website only by defining metadata. Please refer to the section
[**Metadata**](#metadata) to get an idea of pre-defined metadata as well as your
options when defining your own metadata.

With metadata you can define environment variables for a file. You can access
these variables in your markdown source or in HTML templates/snippets by
prepending the variable name with a dollar sign. Please refer to the section
[**Variables**](#variables) for more information on variables.

Note: Kamaji confines its operations to the current working directory.

## Name, Icon, and Development

This program is named after the boiler-grandpa in "Spirited Away" to honour
Hayao Miyazaki and his œuvre.

The Icon represents the letter "K" in the Braille writing system.

The BBC recording of the Last Night of the Proms 2019 supplied the soundtrack
while developing this software. You can't go wrong with a bit of a Cancan.
And with *the* all-time great version of "Somewhere Over the Rainbow", sung so
lushly by Jamie Barton.

## Kamaji Website Repository Layout

During the build process Kamaji creates a hidden data structure, the Kamaji
website repository. Per default it is structured as follows:

 - **.kamaji/** Root of the Kamaji website repository.
 - **.kamaji/out/** Your final website code is placed here.
 - **.kamaji/nodes.json** Combined node structure and environment JSON database.

The JSON database stores the following data on a per-URI base:
	
 - **deps** List of dependency URIs
 - **refs** List of reference URIs
 - **env** Key-value store of the URI's environment

## Workflow

 1. Create a new directory, change into it and create your markdown documents.
    Make sure your main and/or starting document is named `index.md`.
    Kamaji always starts the build process from this file. Kamaji offers a `demo`
    command which populates the current directory with some example files.
 2. Call `build`; Kamaji will process the file `index.md` and will use its
    dependencies and references to explore and build the rest of your site.
 3. Synchronise the contents of ./kamaji/out with your web server directory.
 4. If you need a sitemap or information on your site's link structure, use the
    `map` command. It will generate a GraphViz rendering of your site's *source*
    structure. 

## Markdown Conversion

This program relies on the Python module "markdown" (<https://python-markdown.github.io/>).
It uses the follwing extensions (<https://python-markdown.github.io/extensions/>):

 - **CodeHilite** Syntax highlighting via Pygments.
 - **Meta-Data** Metadata definition and processing.
 - **Sane Lists** Makes list syntax less surprising.
 - **SmartyPants** Transforms straight quotes into HTML quote entities, dashes into en- and em-dashes and three consecutive dots into ellipsis entity. Honours the language, i.e. Germans get their Gänsefüßchen.
 - **Table of Contents** Automatically creates a table of contents from document headings.
 - **Abbreviations** Enables definition of HTML5 abbreviations.
 - **Definition Lists** Enables definition of HTML5 definition lists.
 - **Fenced Code Blocks** Code block can be printed as is with syntax highlighting by fencing them with '```' on the line before and after.
 - **Tables** Create tables with pipes `|` and hyphens `-`, just like on GitHub.

In addition, Kamaji installs its own extension in order to manipulate python-markdown's internal XML tree.
As a side effect, parsing of ~~strike-through text~~ as well as __inserted text__ is made possible.

## Syntax Highlighting

Highlighting of programming language syntax in fenced code blocks needs a 
special CSS file. You can generate one with the following command
(in this example resulting in the creation of code.css):

```bash
pygmentize -S STYLE -f hmtl -a .codehilite > code.css
```

STYLE is a pre-defined style of Pygments. You can obtain an overview of
supported styles with the following command:

```bash
pygmentize -L style
```

## Metadata

You configure a Kamaji instance by defining metadata in its Markdown source
files. During the build process this metadata is made available as variables.

Files named `index.md` define the environment variables for all files in the
same directory and in all subdirectories. Each file might re-define environment
variables using metadata definitions. This way it is possible to re-use
definitions and to create a hierarchical environment. If a subdirectory does not
have an `index.md` the next higher one will be used. If the root
(=current working directory) is reached, the environment will fall back to some
default values. Finally, if no definition is found, the value of a variable
will be set to its name.

Metadata in a Markdown file is defined on the file's first lines by writing
key-value pairs. Keys are single words, consisting of alphanumeric character
plus underscore and dash (`[a-zA-Z0-9_-]`). Keys are case-insensitive and have
to be terminated by a colon. Anything after the colon is treated as the value.
If a line starts with at least four spaces, it is considered to be an additional
value line.

Metadata is terminated by a blank line or malformed keys (e.g. space between key
and colon). Alternatively you can fence Metadata in with lines of three dashes (`---`).

Example code:

```
authorName: Kamaji
auhtorMail: Kamaji@abelbeck.info
```

Kamaji defines the following default keys (given in alphabetical order,
default value in brackets):

 - **createToc** if true, create a table of contents [$createtoc]
 - **dateFormatISO** strftime() format string, ISO date/time format [$dateformatiso]
 - **kamajiName** name of this program [$kamajiname]
 - **kamajiNameFull** full name and version of this program [$kamajinamefull]
 - **kamajiSite** homepage of this program [$kamajisite]
 - **kamajiVersion** version of this program [$kamajiversion]
 - **language** page language, given as ISO 639-1 two-letter code [$language]
 - **timezone** timezone identifier like 'Europe/Berlin' or 'CET' [$timezone]
 - **titleToc** title string of the table of contents [$titletoc]

You are free to define arbitrary metadata as you like. Kamaji will store it as
simple strings, except it encounters certain key name prefixes. In that case it
splits the key name into a prefix and the remaining name as suffix.

The following prefixes are recognised:

 - **dateFormat** Kamaji will parse values of keys with this prefix as
 strftime()-compatible date format strings.
 - **path** Kamaji will interpret values of keys with the prefix `path` as
 local file paths relative to the document they were specified in. If these
 paths define markdown, HTML, CSS, or SVG files, their contents will be available
 in variables with the prefix `html`, `css`, or `svg` respectively.

If Kamaji encounters the key `pathTemplate`, it will use the defined file as an
HTML template to generate the final output. If `pathTemplate` is not defined,
plain markdown HTML output is generated which might not be useful for a website.

Example code, metadata:

```
pathMyPngFile: path/to/file.png
pathMyHtmlFile: path/to/file.html
pathMyMdFile: path/to/file.md
dateFormatISO: %Y-%m-%d
```

Resulting example variables:

```
$$pathMyPngFile  = "path/to/file.png"
$$typeMyPngFile  = "image/png"
$$pathMyHtmlFile = "path/to/file.html"
$$typeMyHtmlFile = "text/html"
$$htmlMyHtmlFile = "<p>Hi!</p>"
$$pathMyMdFile   = "path/to/file.md"
$$typeMyMdFile   = "text/markdown"
$$htmlMyMdFile   = "<p>Hi from Markdown!</p>"
$$dateFormatISO  = "%Y-%m-%d"
$$dateISO        = "2022-02-09"
```

## Variables

Kamaji offers environment variables.

This environment is populated either automatically (date/time and the like) or
by defining it in a file's metadata.

You can integrate these variables into your sources (markdown or HTML) by
specifying their name prepended with a dollar sign. Kamaji will replace the
variable names with the current value during the build process. You can delimit
a variable with braces in order to combine it with valid variable identifer
characters. A literal dollar sign is escaped by specifying it twice.

Kamaji creates some variables automatically:

 - **date** If variables with the prefix `dateFormat` are defined in the metadata,
 Kamaji will create variables with the prefix `date` and the same suffix.
 These hold the modification timestamp of the currently processed document,
 formatted according to the `dateFormat` definition. The currently set timezone
 is applied.
 - **type** Any local path has a MIME type which is stored in variable with
 prefix `type` and the same suffix.
 - **html** Offer the contents of a Markdown or HTML file; a variable with the prefix `path` and the same suffix is needed to provide the file's path.
 - **css** Offer the contents of a CSS file; a variable with the prefix `path` and the same suffix is needed to provide the file's path.
 - **svg** Offer the contents of a SVG file; a variable with the prefix `path` and the same suffix is needed to provide the file's path.
 - **title:** Kamaji will look for the first heading element in an HTML variable
 and will store its contents in a variable with prefix `title` and the same
 suffix. If such a key was already defined via metadata, title extraction is skipped.

Kamaji makes the intermediate HTML code of the currently processed markdown file
as well as its table of contents HTML code available via the automatically generated variables
`htmlContent` and `htmlToc`. Thus the document's title is available as variable `titleContent`,
and the table of content's title can be accessed via `titleToc`. Please note that
any additional content imported through `html*` variables cannot be considered when
building the table of contents, because variables get substituted right before generating the HTML output file.

If the metadata variable `createToc` is set to yes or true, the variable
`htmlToc` is filled with the page's table of contents (as derived from its
headings). Otherwise both `htmlToc` and `titleToc` will be empty. In addition,
`titleToc` will be set to the empty string if `htmlToc` is empty. In combination
with the removal of empty tags (cf. `--no-prune` option) this prevents displaying
an empty table of contents structure.

Example code:

```
<a href="mailto:$authorMail">$authorName</a>
<span>${prefix}suffix</span>
```

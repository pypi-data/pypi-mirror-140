---
pathSitemap: sitemap.gv.svg
createToc: false
---

# How to generate this site

To generate this demo site, create a new directory, change into it and issue
the following commands:

``` bash
kamaji demo
pygmentize -S solarized-dark \
   -f html \
   -a .codehilite > code.css
kamaji --build
kamaji.py map --site --merge sitemap
kamaji --build
```

Explanation:

 1. `demo` creates the demo source files
 2. `pygmentize` creates a CSS file for syntax highlighting
 3. `build` processes all source and dependency files and creates the output
 4. `map` generates a sitemap
 5. `build` rebuilds the output and now also integrates the sitemap

# Example Sitemap

The `map` command generates the following SVG sitemap, which is integrated into this page using a variable `$$svgSitemap`.

$svgSitemap

/**
 * @file
 * @author Frank Abelbeck <frank@abelbeck.info>
 * @version 20220204
 * 
 * @section License
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * 
 * @section Description
 * 
 * Javascript for Frank's code simthy website
 */


/** Toggle display style of main>nav>div>ul element between states "none" and "block".
 */
function funToggleToc() {
	let elementList = document.querySelector("main > nav > div > ul");
	let elementHeading = document.querySelector("main > nav > h4");
	if (elementList.style.display == "none") {
		elementList.style.display = "block";
		elementHeading.classList.add("tocHeadingOpened");
		elementHeading.classList.remove("tocHeadingClosed");
	} else {
		elementList.style.display = "none";
		elementHeading.classList.add("tocHeadingClosed");
		elementHeading.classList.remove("tocHeadingOpened");
	}
}

/** Process a media query state transition with regard to a table of contents.
 * 
 * @param elementHeading An Element; heading element of a table of contents
 * @param elementList An Element; list element of a table of contents
 * @param query A MediaQueryList object.
 */
function funToCMediaQuery(elementHeading,elementList,query) {
	if (query.matches) {
		// media query matches, i.e. minimum width is large enough:
		// remove click listener and make sure that nav is visible
		// reset cursor type
		elementHeading.removeEventListener("click",funToggleToc);
		elementHeading.classList.remove("tocHeadingOpened");
		elementHeading.classList.remove("tocHeadingClosed");
		elementList.style.display = "block";
	} else {
		// media query doesn't match, i.e. minimum width is smaller:
		// add click listener
		// set cursor type to pointer (mark as clickable)
		elementHeading.addEventListener("click",funToggleToc);
		elementList.style.display = "none";
		elementHeading.classList.add("tocHeadingClosed");
		elementHeading.classList.remove("tocHeadingOpened");
	}
}


/** Process a intersection observer state change.
 * 
 * Set opacity of all visible table of contents items to 1, otherwise to 0.3.
 * 
 * @param mapElements A map, mapping heading identifiers to list item Elements
 * @param entries A list of IntersectionObserverEntry objects
 */
function funToCIntersection(mapElements,entries) {
	let entriesVisible = [];
	for (let i=0; i<entries.length; ++i) {
		let entry = entries[i];
		if (entry.isIntersecting) {
			// entry in viewport (100 % visible)
			mapElements.get(entry.target.id).style.opacity = 1.0;
		} else {
			// entry leaves viewport (100 % invisible)
			if (entry.boundingClientRect.top < entry.rootBounds.top) {
				// entry leaves to the top: keep toc item highlighted,
				// reduce opacity of predecessor in toc
				mapElements.get(entry.target.id).style.opacity = 1.0;
				let keys = Array.from(mapElements.keys());
				let i = keys.indexOf(entry.target.id);
				if (i > 0) {
					mapElements.get(keys[i-1]).style.opacity = 0.3;
				}
			} else {
				mapElements.get(entry.target.id).style.opacity = 0.3;
			}
		}
	}
}

/** Initialise all other functions/listeners; expected to be run after DOM is set up.
 */
function funDOMLoaded() {
	// make table of contents header clickable
	// observe intersection of viewport with headings
	let elementToCHeader = document.querySelector("main > nav > h4");
	if (elementToCHeader) {
		// create media query watcher and apply initial query
		let mediaQuery = window.matchMedia("(min-width: 60em)");
		let elementToCList = document.querySelector("main > nav > div > ul");
		funToCMediaQuery(elementToCHeader,elementToCList,mediaQuery);
		mediaQuery.addListener(funToCMediaQuery.bind(null,elementToCHeader,elementToCList));
		
		let lstElementsToc = document.querySelectorAll("main > nav li > a");
		let lstElementsHeading = document.querySelectorAll("main > article h1[id], main > article h2[id], main > article h3[id], main > article h4[id], main > article h5[id], main > article h6[id]")
		let mapElements = new Map();
		for (let i=0; i<lstElementsToc.length; ++i) {
			href = lstElementsToc[i].href;
			mapElements.set(href.substring(href.lastIndexOf("#")+1), lstElementsToc[i]);
		}
		
		let observerScrollSpy = new IntersectionObserver(funToCIntersection.bind(null,mapElements),{threshold:1.0});
		for (let i=0; i<lstElementsHeading.length; ++i) {
			observerScrollSpy.observe(lstElementsHeading[i]);
		}
	}
}

document.addEventListener("DOMContentLoaded",funDOMLoaded)

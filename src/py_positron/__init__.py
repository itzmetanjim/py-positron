__version__ = "0.0.2.3" 
import webview
import os
import threading
import re
import importlib
import json
import traceback
import sys
import html
from typing import Callable, Optional
class PositronWindowWrapper:
    """Wrapper for a PyPositron window with event loop thread and context."""
    def __init__(self, window, context, main_thread):
        self.window: webview.Window = window
        self.context: PositronContext = context
        self.document = Document(window)
        self.exposed = ExposedFunctions(context.exposed_functions)
        self.event_thread: threading.Thread = main_thread
        self.htmlwindow = HTMLWindow(window)

def escape_js_string(string: str) -> str:
    """Escape string for JavaScript"""
    return string.replace("\\", "\\\\").replace("\"", "\\\"").replace("\'", "\\'").replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t").replace("\f", "\\f").replace("\v", "\\v")

class PositronContext:
    def __init__(self, window):
        self.window = window
        self.globals = {}
        self.locals = {}
        self.exposed_functions = {}
        self.event_handlers = {}
        
    def __setattr__(self, name, value):
        """Allow dynamic attribute assignment"""
        object.__setattr__(self, name, value)
    def execute(self, code):
        try:
            self.locals.update({
                "window": self.window,
                "document":Document(self.window),
                "exposed": ExposedFunctions(self.exposed_functions),
                "import_module": importlib.import_module,
            })
            exec(code, self.globals, self.locals)
            self.globals.update(self.locals) #...
            return True, None
        except Exception as e:
            error_info = traceback.format_exc()
            return False, error_info
    def register_event_handler(self, element_id, event_type, callback):
        
        key = f"{element_id}_{event_type}"
        callback_globals = dict(self.globals)  
        callback_locals = dict(self.locals)    
        callback_func = callback
        exposed_functions = self.exposed_functions
        
  
        def wrapped_callback():
            try:
                exec_globals = dict(callback_globals)
                exec_locals = dict(callback_locals)
                important_stuff={
                    "window": self.window,
                    "document": Document(self.window),
                    "exposed": ExposedFunctions(exposed_functions),
                    "callback_func": callback_func
                }
                exec_globals.update(important_stuff)
                exec_locals.update(important_stuff)
                exec_code = "def _executor():\n    return callback_func()"
                exec(exec_code, exec_globals, exec_locals)
                result = exec_locals["_executor"]()
                return result
            except Exception as e:
                print(f"Error in event handler: {e}")
                traceback.print_exc()
                return str(e)
        self.event_handlers[key] = wrapped_callback
        return key
class Element:
    def __init__(self, window, js_path):
        self.window = window
        self.js_path = js_path

    # Properties
    @property
    def accessKey(self) -> str:
        """Sets or returns the accesskey attribute of an element"""
        return self.window.evaluate_js(f'{self.js_path}.accessKey')
    
    @accessKey.setter
    def accessKey(self, value: str):
        """Sets the accesskey attribute of an element"""
        self.window.evaluate_js(f'{self.js_path}.accessKey = {json.dumps(value)}')
    
    @property
    def attributes(self):
        """Returns a NamedNodeMap of an element's attributes"""
        return self.window.evaluate_js(f'{self.js_path}.attributes')
    
    @property
    def childElementCount(self) -> int:
        """Returns an element's number of child elements"""
        return self.window.evaluate_js(f'{self.js_path}.childElementCount') or 0
    
    @property
    def childNodes(self):
        """Returns a NodeList of an element's child nodes"""
        return ElementList(self.window, f'{self.js_path}.childNodes')
    
    @property
    def children(self):
        """Returns an HTMLCollection of an element's child elements"""
        return ElementList(self.window, f'{self.js_path}.children')
    
    @property
    def classList(self):
        """Returns the class name(s) of an element"""
        return self.window.evaluate_js(f'{self.js_path}.classList')
    
    @property
    def className(self) -> str:
        """Sets or returns the value of the class attribute of an element"""
        return self.window.evaluate_js(f'{self.js_path}.className')
    
    @className.setter
    def className(self, value: str):
        """Sets the value of the class attribute of an element"""
        self.window.evaluate_js(f'{self.js_path}.className = {json.dumps(value)}')
    
    @property
    def clientHeight(self) -> int:
        """Returns the height of an element, including padding"""
        return self.window.evaluate_js(f'{self.js_path}.clientHeight') or 0
    
    @property
    def clientLeft(self) -> int:
        """Returns the width of the left border of an element"""
        return self.window.evaluate_js(f'{self.js_path}.clientLeft') or 0
    
    @property
    def clientTop(self) -> int:
        """Returns the width of the top border of an element"""
        return self.window.evaluate_js(f'{self.js_path}.clientTop') or 0
    
    @property
    def clientWidth(self) -> int:
        """Returns the width of an element, including padding"""
        return self.window.evaluate_js(f'{self.js_path}.clientWidth') or 0
    
    @property
    def contentEditable(self) -> str:
        """Sets or returns whether the content of an element is editable or not"""
        return self.window.evaluate_js(f'{self.js_path}.contentEditable')
    
    @contentEditable.setter
    def contentEditable(self, value: str):
        """Sets whether the content of an element is editable or not"""
        self.window.evaluate_js(f'{self.js_path}.contentEditable = {json.dumps(value)}')
    
    @property
    def dir(self) -> str:
        """Sets or returns the value of the dir attribute of an element"""
        return self.window.evaluate_js(f'{self.js_path}.dir')
    
    @dir.setter
    def dir(self, value: str):
        """Sets the value of the dir attribute of an element"""
        self.window.evaluate_js(f'{self.js_path}.dir = {json.dumps(value)}')
    
    @property
    def firstChild(self):
        """Returns the first child node of an element"""
        return Element(self.window, f'{self.js_path}.firstChild')
    
    @property
    def firstElementChild(self):
        """Returns the first child element of an element"""
        return Element(self.window, f'{self.js_path}.firstElementChild')
    
    @property
    def id(self) -> str:
        """Sets or returns the value of the id attribute of an element"""
        return self.window.evaluate_js(f'{self.js_path}.id')
    
    @id.setter
    def id(self, value: str):
        """Sets the value of the id attribute of an element"""
        self.window.evaluate_js(f'{self.js_path}.id = {json.dumps(value)}')
    
    @property
    def isContentEditable(self) -> bool:
        """Returns true if an element's content is editable"""
        return self.window.evaluate_js(f'{self.js_path}.isContentEditable')
    
    @property
    def lang(self) -> str:
        """Sets or returns the value of the lang attribute of an element"""
        return self.window.evaluate_js(f'{self.js_path}.lang')
    
    @lang.setter
    def lang(self, value: str):
        """Sets the value of the lang attribute of an element"""
        self.window.evaluate_js(f'{self.js_path}.lang = {json.dumps(value)}')
    
    @property
    def lastChild(self):
        """Returns the last child node of an element"""
        return Element(self.window, f'{self.js_path}.lastChild')
    
    @property
    def lastElementChild(self):
        """Returns the last child element of an element"""
        return Element(self.window, f'{self.js_path}.lastElementChild')
    
    @property
    def namespaceURI(self) -> str:
        """Returns the namespace URI of an element"""
        return self.window.evaluate_js(f'{self.js_path}.namespaceURI')
    
    @property
    def nextSibling(self):
        """Returns the next node at the same node tree level"""
        return Element(self.window, f'{self.js_path}.nextSibling')
    
    @property
    def nextElementSibling(self):
        """Returns the next element at the same node tree level"""
        return Element(self.window, f'{self.js_path}.nextElementSibling')
    
    @property
    def nodeName(self) -> str:
        """Returns the name of a node"""
        return self.window.evaluate_js(f'{self.js_path}.nodeName')
    
    @property
    def nodeType(self) -> int:
        """Returns the node type of a node"""
        return self.window.evaluate_js(f'{self.js_path}.nodeType') or 0
    
    @property
    def nodeValue(self) -> str:
        """Sets or returns the value of a node"""
        return self.window.evaluate_js(f'{self.js_path}.nodeValue')
    
    @nodeValue.setter
    def nodeValue(self, value: str):
        """Sets the value of a node"""
        self.window.evaluate_js(f'{self.js_path}.nodeValue = {json.dumps(value)}')
    
    @property
    def offsetHeight(self) -> int:
        """Returns the height of an element, including padding, border and scrollbar"""
        return self.window.evaluate_js(f'{self.js_path}.offsetHeight') or 0
    
    @property
    def offsetWidth(self) -> int:
        """Returns the width of an element, including padding, border and scrollbar"""
        return self.window.evaluate_js(f'{self.js_path}.offsetWidth') or 0
    
    @property
    def offsetLeft(self) -> int:
        """Returns the horizontal offset position of an element"""
        return self.window.evaluate_js(f'{self.js_path}.offsetLeft') or 0
    
    @property
    def offsetParent(self):
        """Returns the offset container of an element"""
        return Element(self.window, f'{self.js_path}.offsetParent')
    
    @property
    def offsetTop(self) -> int:
        """Returns the vertical offset position of an element"""
        return self.window.evaluate_js(f'{self.js_path}.offsetTop') or 0
    
    @property
    def outerHTML(self) -> str:
        """Sets or returns the content of an element (including the start tag and the end tag)"""
        return self.window.evaluate_js(f'{self.js_path}.outerHTML')
    
    @outerHTML.setter
    def outerHTML(self, value: str):
        """Sets the content of an element (including the start tag and the end tag)"""
        self.window.evaluate_js(f'{self.js_path}.outerHTML = {json.dumps(value)}')
    
    @property
    def outerText(self) -> str:
        """Sets or returns the outer text content of a node and its descendants"""
        return self.window.evaluate_js(f'{self.js_path}.outerText')
    
    @outerText.setter
    def outerText(self, value: str):
        """Sets the outer text content of a node and its descendants"""
        self.window.evaluate_js(f'{self.js_path}.outerText = {json.dumps(value)}')
    
    @property
    def ownerDocument(self):
        """Returns the root element (document object) for an element"""
        return self.window.evaluate_js(f'{self.js_path}.ownerDocument')
    
    @property
    def parentNode(self):
        """Returns the parent node of an element"""
        return Element(self.window, f'{self.js_path}.parentNode')
    
    @property
    def parentElement(self):
        """Returns the parent element node of an element"""
        return Element(self.window, f'{self.js_path}.parentElement')
    
    @property
    def previousSibling(self):
        """Returns the previous node at the same node tree level"""
        return Element(self.window, f'{self.js_path}.previousSibling')
    
    @property
    def previousElementSibling(self):
        """Returns the previous element at the same node tree level"""
        return Element(self.window, f'{self.js_path}.previousElementSibling')
    
    @property
    def scrollHeight(self) -> int:
        """Returns the entire height of an element, including padding"""
        return self.window.evaluate_js(f'{self.js_path}.scrollHeight') or 0
    
    @property
    def scrollLeft(self) -> int:
        """Sets or returns the number of pixels an element's content is scrolled horizontally"""
        return self.window.evaluate_js(f'{self.js_path}.scrollLeft') or 0
    
    @scrollLeft.setter
    def scrollLeft(self, value: int):
        """Sets the number of pixels an element's content is scrolled horizontally"""
        self.window.evaluate_js(f'{self.js_path}.scrollLeft = {value}')
    
    @property
    def scrollTop(self) -> int:
        """Sets or returns the number of pixels an element's content is scrolled vertically"""
        return self.window.evaluate_js(f'{self.js_path}.scrollTop') or 0
    
    @scrollTop.setter
    def scrollTop(self, value: int):
        """Sets the number of pixels an element's content is scrolled vertically"""
        self.window.evaluate_js(f'{self.js_path}.scrollTop = {value}')
    
    @property
    def scrollWidth(self) -> int:
        """Returns the entire width of an element, including padding"""
        return self.window.evaluate_js(f'{self.js_path}.scrollWidth') or 0
    
    @property
    def tabIndex(self) -> int:
        """Sets or returns the value of the tabindex attribute of an element"""
        return self.window.evaluate_js(f'{self.js_path}.tabIndex') or 0
    
    @tabIndex.setter
    def tabIndex(self, value: int):
        """Sets the value of the tabindex attribute of an element"""
        self.window.evaluate_js(f'{self.js_path}.tabIndex = {value}')
    
    @property
    def tagName(self) -> str:
        """Returns the tag name of an element"""
        return self.window.evaluate_js(f'{self.js_path}.tagName')
    
    @property
    def textContent(self) -> str:
        """Sets or returns the textual content of a node and its descendants"""
        return self.window.evaluate_js(f'{self.js_path}.textContent')
    
    @textContent.setter
    def textContent(self, value: str):
        """Sets the textual content of a node and its descendants"""
        self.window.evaluate_js(f'{self.js_path}.textContent = {json.dumps(value)}')
    
    @property
    def title(self) -> str:
        """Sets or returns the value of the title attribute of an element"""
        return self.window.evaluate_js(f'{self.js_path}.title')
    
    @title.setter
    def title(self, value: str):
        """Sets the value of the title attribute of an element"""
        self.window.evaluate_js(f'{self.js_path}.title = {json.dumps(value)}')

    # Existing properties
    @property
    def innerText(self) -> str:
        """Get inner text"""
        return self.window.evaluate_js(f'{self.js_path}.innerText')
    @innerText.setter
    def innerText(self, value):
        """Set inner text"""
        self.window.evaluate_js(f'{self.js_path}.innerText = {json.dumps(value)}')
    
    @property
    def innerHTML(self) -> str:
        """Get inner HTML"""
        return self.window.evaluate_js(f'{self.js_path}.innerHTML')
    @innerHTML.setter
    def innerHTML(self, value):
        """Set inner HTML - Warning: this can lead to XSS vulnerabilities if not sanitized properly. Use with caution."""
        self.window.evaluate_js(f'{self.js_path}.innerHTML = {json.dumps(value)}')
    
    @property
    def value(self):
        """Get value of form element."""
        return self.window.evaluate_js(f'{self.js_path}.value')
    @value.setter
    def value(self, value):
        """Set value of form element."""
        self.window.evaluate_js(f'{self.js_path}.value = {json.dumps(value)}')
    
    @property
    def style(self):
        """Get style object"""
        return Style(self.window, f'{self.js_path}.style')

    # Methods
    def after(self, *nodes):
        """Inserts one or more nodes (elements) or strings after an element"""
        for node in nodes:
            if isinstance(node, Element):
                self.window.evaluate_js(f'{self.js_path}.after({node.js_path})')
            else:
                self.window.evaluate_js(f'{self.js_path}.after({json.dumps(str(node))})')
    
    def append(self, *nodes):
        """Adds (appends) one or several nodes (element) or strings after the last child of an element"""
        for node in nodes:
            if isinstance(node, Element):
                self.window.evaluate_js(f'{self.js_path}.append({node.js_path})')
            else:
                self.window.evaluate_js(f'{self.js_path}.append({json.dumps(str(node))})')
    
    def before(self, *nodes):
        """Inserts one or more nodes (elements) or strings before an element"""
        for node in nodes:
            if isinstance(node, Element):
                self.window.evaluate_js(f'{self.js_path}.before({node.js_path})')
            else:
                self.window.evaluate_js(f'{self.js_path}.before({json.dumps(str(node))})')
    
    def blur(self):
        """Removes focus from an element"""
        self.window.evaluate_js(f'{self.js_path}.blur()')
    
    def click(self):
        """Simulates a mouse-click on an element"""
        self.window.evaluate_js(f'{self.js_path}.click()')
    
    def cloneNode(self, deep: bool = False):
        """Clones an element"""
        return Element(self.window, f'{self.js_path}.cloneNode({json.dumps(deep)})')
    
    def closest(self, selector: str):
        """Searches the DOM tree for the closest element that matches a CSS selector"""
        return Element(self.window, f'{self.js_path}.closest({json.dumps(selector)})')
    
    def compareDocumentPosition(self, other):
        """Compares the document position of two elements"""
        if isinstance(other, Element):
            return self.window.evaluate_js(f'{self.js_path}.compareDocumentPosition({other.js_path})')
        else:
            raise TypeError("compareDocumentPosition expects an Element")
    
    def contains(self, other):
        """Returns true if a node is a descendant of a node"""
        if isinstance(other, Element):
            return self.window.evaluate_js(f'{self.js_path}.contains({other.js_path})')
        else:
            raise TypeError("contains expects an Element")
    
    def focus(self):
        """Gives focus to an element"""
        self.window.evaluate_js(f'{self.js_path}.focus()')
    
    def getAttribute(self, name: str) -> str:
        """Returns the value of an element's attribute"""
        return self.window.evaluate_js(f'{self.js_path}.getAttribute({json.dumps(name)})')
    
    def getAttributeNode(self, name: str):
        """Returns an attribute node"""
        return self.window.evaluate_js(f'{self.js_path}.getAttributeNode({json.dumps(name)})')
    
    def getBoundingClientRect(self):
        """Returns the size of an element and its position relative to the viewport"""
        return self.window.evaluate_js(f'{self.js_path}.getBoundingClientRect()')
    
    def getElementsByClassName(self, class_name: str):
        """Returns a collection of child elements with a given class name"""
        return ElementList(self.window, f'{self.js_path}.getElementsByClassName({json.dumps(class_name)})')
    
    def getElementsByTagName(self, tag_name: str):
        """Returns a collection of child elements with a given tag name"""
        return ElementList(self.window, f'{self.js_path}.getElementsByTagName({json.dumps(tag_name)})')
    
    def hasAttribute(self, name: str) -> bool:
        """Returns true if an element has a given attribute"""
        return self.window.evaluate_js(f'{self.js_path}.hasAttribute({json.dumps(name)})')
    
    def hasAttributes(self) -> bool:
        """Returns true if an element has any attributes"""
        return self.window.evaluate_js(f'{self.js_path}.hasAttributes()')
    
    def hasChildNodes(self) -> bool:
        """Returns true if an element has any child nodes"""
        return self.window.evaluate_js(f'{self.js_path}.hasChildNodes()')
    
    def insertAdjacentElement(self, position: str, element):
        """Inserts a new HTML element at a position relative to an element"""
        if isinstance(element, Element):
            return Element(self.window, f'{self.js_path}.insertAdjacentElement({json.dumps(position)}, {element.js_path})')
        else:
            raise TypeError("insertAdjacentElement expects an Element")
    
    def insertAdjacentHTML(self, position: str, html: str):
        """Inserts an HTML formatted text at a position relative to an element"""
        self.window.evaluate_js(f'{self.js_path}.insertAdjacentHTML({json.dumps(position)}, {json.dumps(html)})')
    
    def insertAdjacentText(self, position: str, text: str):
        """Inserts text into a position relative to an element"""
        self.window.evaluate_js(f'{self.js_path}.insertAdjacentText({json.dumps(position)}, {json.dumps(text)})')
    
    def insertBefore(self, new_node, reference_node):
        """Inserts a new child node before an existing child node"""
        if isinstance(new_node, Element) and isinstance(reference_node, Element):
            return Element(self.window, f'{self.js_path}.insertBefore({new_node.js_path}, {reference_node.js_path})')
        else:
            raise TypeError("insertBefore expects Element objects")
    
    def isDefaultNamespace(self, namespace_uri: str) -> bool:
        """Returns true if a given namespaceURI is the default"""
        return self.window.evaluate_js(f'{self.js_path}.isDefaultNamespace({json.dumps(namespace_uri)})')
    
    def isEqualNode(self, other):
        """Checks if two elements are equal"""
        if isinstance(other, Element):
            return self.window.evaluate_js(f'{self.js_path}.isEqualNode({other.js_path})')
        else:
            raise TypeError("isEqualNode expects an Element")
    
    def isSameNode(self, other):
        """Checks if two elements are the same node"""
        if isinstance(other, Element):
            return self.window.evaluate_js(f'{self.js_path}.isSameNode({other.js_path})')
        else:
            raise TypeError("isSameNode expects an Element")
    
    def matches(self, selector: str) -> bool:
        """Returns true if an element is matched by a given CSS selector"""
        return self.window.evaluate_js(f'{self.js_path}.matches({json.dumps(selector)})')
    
    def normalize(self):
        """Joins adjacent text nodes and removes empty text nodes in an element"""
        self.window.evaluate_js(f'{self.js_path}.normalize()')
    
    def querySelector(self, selector: str):
        """Returns the first child element that matches a CSS selector(s)"""
        return Element(self.window, f'{self.js_path}.querySelector({json.dumps(selector)})')
    
    def querySelectorAll(self, selector: str):
        """Returns all child elements that matches a CSS selector(s)"""
        return ElementList(self.window, f'{self.js_path}.querySelectorAll({json.dumps(selector)})')
    
    def remove(self):
        """Removes an element from the DOM"""
        self.window.evaluate_js(f'{self.js_path}.remove()')
    
    def removeAttribute(self, name: str):
        """Removes an attribute from an element"""
        self.window.evaluate_js(f'{self.js_path}.removeAttribute({json.dumps(name)})')
    
    def removeAttributeNode(self, attr_node):
        """Removes an attribute node, and returns the removed node"""
        return self.window.evaluate_js(f'{self.js_path}.removeAttributeNode({attr_node})')
    
    def removeEventListener(self, event_type: str, callback=None):
        """Removes an event handler that has been attached with the addEventListener() method"""
        # Get element ID for handler removal
        element_id = self.window.evaluate_js(f"""
            (function() {{
                var el = {self.js_path};
                return el ? (el.id || 'anonymous_' + Math.random().toString(36).substr(2, 9)) : null;
            }})()
        """)
        
        if element_id and hasattr(self.window, '_py_context'):
            key = f"{element_id}_{event_type}"
            if key in self.window._py_context.event_handlers:
                del self.window._py_context.event_handlers[key]
        
        # Note: JavaScript removeEventListener requires the exact same function reference
        # This is a simplified implementation
        js_code = f"""
        console.log("removeEventListener called for {event_type} on element");
        """
        self.window.evaluate_js(js_code)
    
    def scrollIntoView(self, align_to_top: bool = True):
        """Scrolls the element into the visible area of the browser window"""
        self.window.evaluate_js(f'{self.js_path}.scrollIntoView({json.dumps(align_to_top)})')
    
    def setAttributeNode(self, attr_node):
        """Sets or changes an attribute node"""
        return self.window.evaluate_js(f'{self.js_path}.setAttributeNode({attr_node})')
    
    def toString(self) -> str:
        """Converts an element to a string"""
        return self.window.evaluate_js(f'{self.js_path}.toString()')

    # Existing methods
    def setAttribute(self, attr_name, value):
        """Set attribute"""
        self.window.evaluate_js(f'{self.js_path}.setAttribute("{attr_name}", {json.dumps(value)})')
    
    def appendChild(self, child):
        """Append child"""
        if isinstance(child, Element):
            self.window.evaluate_js(f'{self.js_path}.appendChild({child.js_path})')
        else:
            raise TypeError("appendChild expects an Element")
    def removeChild(self, child):
        """Remove child"""
        if isinstance(child, Element):
            self.window.evaluate_js(f'{self.js_path}.removeChild({child.js_path})')
        else:
            raise TypeError("removeChild expects an Element")
    
    def replaceChild(self, new_child, old_child):
        """Replace child"""
        if isinstance(new_child, Element) and isinstance(old_child, Element):
            self.window.evaluate_js(f'{self.js_path}.replaceChild({new_child.js_path}, {old_child.js_path})')
        else:
            raise TypeError("replaceChild expects Element objects")
    
    def addEventListener(self, event_type, callback)-> bool:
        """Add event listener. Returns success. Example:
        >>> element.addEventListener("click",callback_function)
        -> True (if successful)"""
        
        element_id = self.window.evaluate_js(f"""
            (function() {{
                var el = {self.js_path};
                return el ? (el.id || 'anonymous_' + Math.random().toString(36).substr(2, 9)) : null;
            }})()
        """)
        
        if not element_id:
            print(f"WARNING: Could not get ID for element: {self.js_path}")
            return False
        
        # Get the PyContext from the window
        context = None
        if hasattr(self.window, '_py_context'):
            context = self.window._py_context
        
        if not context:
            # If no context found, create a temporary one just for this handler
            context = PositronContext(self.window)
            self.window._py_context = context
            
        # Register the event handler with the context
        handler_key = context.register_event_handler(element_id, event_type, callback)
        
        # Create global event handler if not already created
        if not hasattr(self.window, 'handle_py_event'):
            def handle_py_event(element_id, event_type):
                key = f"{element_id}_{event_type}"
                if hasattr(self.window, '_py_context') and key in self.window._py_context.event_handlers:
                    try:
                        return self.window._py_context.event_handlers[key]()
                    except Exception as e:
                        print(f"[ERROR] handling event: {e}")
                        traceback.print_exc()
                        return str(e)
                print(f"WARNING: No handler found for {key}")
                return False
                
            self.window.handle_py_event = handle_py_event
            self.window.expose(handle_py_event)
        
        # Add the event listener in JavaScript
        js_code = f"""
        (function() {{
            var element = {self.js_path};
            if (!element) return false;
            
            element.addEventListener("{event_type}", function(event) {{
                console.log("Event triggered: {event_type} on {element_id}");
                window.pywebview.api.handle_py_event("{element_id}", "{event_type}");
            }});
            return true;
        }})();
        """
        
        success = self.window.evaluate_js(js_code)
        
        return success
class Style:
    def __init__(self, window, js_path):
        self.window = window
        self.js_path = js_path
    
    def __setattr__(self, name, value):
        if name in ['window', 'js_path']:
            super().__setattr__(name, value)
        else:
            self.window.evaluate_js(f'{self.js_path}.{name} = {json.dumps(value)}')
    def __getattr__(self, name):
        return self.window.evaluate_js(f'{self.js_path}.{name}')
    
class ElementList:
    def __init__(self, window, js_path):
        self.window = window
        self.js_path = js_path
        self.length = self.window.evaluate_js(f'{self.js_path}.length') or 0
    def __getitem__(self, index):
        if 0 <= index < self.length:
            return Element(self.window, f'{self.js_path}[{index}]')
        raise IndexError("ElementList index out of range")
    def __len__(self):
        return self.length
    
    def __iter__(self):
        for i in range(self.length):
            yield self[i]
            yield self[i]

class Console:
    """Console object for debugging and logging"""
    def __init__(self, window):
        self.window = window
    
    def assert_(self, assertion, *message):
        """Writes an error message to the console if a assertion is false"""
        if not assertion:
            msg = ' '.join(str(arg) for arg in message) if message else 'Assertion failed'
            self.window.evaluate_js(f'console.assert({json.dumps(assertion)}, {json.dumps(msg)})')
    
    def clear(self):
        """Clears the console"""
        self.window.evaluate_js('console.clear()')
    
    def count(self, label='default'):
        """Logs the number of times that this particular call to count() has been called"""
        self.window.evaluate_js(f'console.count({json.dumps(label)})')
    
    def error(self, *args):
        """Outputs an error message to the console"""
        message = ' '.join(str(arg) for arg in args)
        self.window.evaluate_js(f'console.error({json.dumps(message)})')
    
    def group(self, *args):
        """Creates a new inline group in the console"""
        message = ' '.join(str(arg) for arg in args) if args else ''
        self.window.evaluate_js(f'console.group({json.dumps(message)})')
    
    def groupCollapsed(self, *args):
        """Creates a new inline group in the console, but collapsed"""
        message = ' '.join(str(arg) for arg in args) if args else ''
        self.window.evaluate_js(f'console.groupCollapsed({json.dumps(message)})')
    
    def groupEnd(self):
        """Exits the current inline group in the console"""
        self.window.evaluate_js('console.groupEnd()')
    
    def info(self, *args):
        """Outputs an informational message to the console"""
        message = ' '.join(str(arg) for arg in args)
        self.window.evaluate_js(f'console.info({json.dumps(message)})')
    
    def log(self, *args):
        """Outputs a message to the console"""
        message = ' '.join(str(arg) for arg in args)
        self.window.evaluate_js(f'console.log({json.dumps(message)})')
    
    def table(self, data):
        """Displays tabular data as a table"""
        self.window.evaluate_js(f'console.table({json.dumps(data)})')
    
    def time(self, label='default'):
        """Starts a timer"""
        self.window.evaluate_js(f'console.time({json.dumps(label)})')
    
    def timeEnd(self, label='default'):
        """Stops a timer that was previously started by console.time()"""
        self.window.evaluate_js(f'console.timeEnd({json.dumps(label)})')
    
    def trace(self, *args):
        """Outputs a stack trace to the console"""
        message = ' '.join(str(arg) for arg in args) if args else ''
        self.window.evaluate_js(f'console.trace({json.dumps(message)})')
    
    def warn(self, *args):
        """Outputs a warning message to the console"""
        message = ' '.join(str(arg) for arg in args)
        self.window.evaluate_js(f'console.warn({json.dumps(message)})')

class History:
    """History object for navigation"""
    def __init__(self, window):
        self.window = window
    
    @property
    def length(self) -> int:
        """Returns the number of URLs (pages) in the history list"""
        return self.window.evaluate_js('history.length') or 0
    
    def back(self):
        """Loads the previous URL (page) in the history list"""
        self.window.evaluate_js('history.back()')
    
    def forward(self):
        """Loads the next URL (page) in the history list"""
        self.window.evaluate_js('history.forward()')
    
    def go(self, number: int):
        """Loads a specific URL (page) from the history list"""
        self.window.evaluate_js(f'history.go({number})')

class Location:
    """Location object for URL manipulation"""
    def __init__(self, window):
        self.window = window
    
    @property
    def hash(self) -> str:
        """Sets or returns the anchor part (#) of a URL"""
        return self.window.evaluate_js('location.hash') or ''
    
    @hash.setter
    def hash(self, value: str):
        """Sets the anchor part (#) of a URL"""
        self.window.evaluate_js(f'location.hash = {json.dumps(value)}')
    
    @property
    def host(self) -> str:
        """Sets or returns the hostname and port number of a URL"""
        return self.window.evaluate_js('location.host') or ''
    
    @host.setter
    def host(self, value: str):
        """Sets the hostname and port number of a URL"""
        self.window.evaluate_js(f'location.host = {json.dumps(value)}')
    
    @property
    def hostname(self) -> str:
        """Sets or returns the hostname of a URL"""
        return self.window.evaluate_js('location.hostname') or ''
    
    @hostname.setter
    def hostname(self, value: str):
        """Sets the hostname of a URL"""
        self.window.evaluate_js(f'location.hostname = {json.dumps(value)}')
    
    @property
    def href(self) -> str:
        """Sets or returns the entire URL"""
        return self.window.evaluate_js('location.href') or ''
    
    @href.setter
    def href(self, value: str):
        """Sets the entire URL"""
        self.window.evaluate_js(f'location.href = {json.dumps(value)}')
    
    @property
    def origin(self) -> str:
        """Returns the protocol, hostname and port number of a URL"""
        return self.window.evaluate_js('location.origin') or ''
    
    @property
    def pathname(self) -> str:
        """Sets or returns the path name of a URL"""
        return self.window.evaluate_js('location.pathname') or ''
    
    @pathname.setter
    def pathname(self, value: str):
        """Sets the path name of a URL"""
        self.window.evaluate_js(f'location.pathname = {json.dumps(value)}')
    
    @property
    def port(self) -> str:
        """Sets or returns the port number of a URL"""
        return self.window.evaluate_js('location.port') or ''
    
    @port.setter
    def port(self, value: str):
        """Sets the port number of a URL"""
        self.window.evaluate_js(f'location.port = {json.dumps(value)}')
    
    @property
    def protocol(self) -> str:
        """Sets or returns the protocol of a URL"""
        return self.window.evaluate_js('location.protocol') or ''
    
    @protocol.setter
    def protocol(self, value: str):
        """Sets the protocol of a URL"""
        self.window.evaluate_js(f'location.protocol = {json.dumps(value)}')
    
    @property
    def search(self) -> str:
        """Sets or returns the querystring part of a URL"""
        return self.window.evaluate_js('location.search') or ''
    
    @search.setter
    def search(self, value: str):
        """Sets the querystring part of a URL"""
        self.window.evaluate_js(f'location.search = {json.dumps(value)}')
    
    def assign(self, url: str):
        """Loads a new document"""
        self.window.evaluate_js(f'location.assign({json.dumps(url)})')
    
    def reload(self, force_reload: bool = False):
        """Reloads the current document"""
        self.window.evaluate_js(f'location.reload({json.dumps(force_reload)})')
    
    def replace(self, url: str):
        """Replaces the current document with a new one"""
        self.window.evaluate_js(f'location.replace({json.dumps(url)})')

class Navigator:
    """Navigator object for browser information"""
    def __init__(self, window):
        self.window = window
    
    @property
    def appCodeName(self) -> str:
        """Returns the application code name of the browser"""
        return self.window.evaluate_js('navigator.appCodeName') or ''
    
    @property
    def appName(self) -> str:
        """Returns the application name of the browser"""
        return self.window.evaluate_js('navigator.appName') or ''
    
    @property
    def appVersion(self) -> str:
        """Returns the version information of the browser"""
        return self.window.evaluate_js('navigator.appVersion') or ''
    
    @property
    def cookieEnabled(self) -> bool:
        """Returns true if browser cookies are enabled"""
        return self.window.evaluate_js('navigator.cookieEnabled') or False
    
    @property
    def geolocation(self):
        """Returns a geolocation object for the user's location"""
        return self.window.evaluate_js('navigator.geolocation')
    
    @property
    def language(self) -> str:
        """Returns browser language"""
        return self.window.evaluate_js('navigator.language') or ''
    
    @property
    def onLine(self) -> bool:
        """Returns true if the browser is online"""
        return self.window.evaluate_js('navigator.onLine') or False
    
    @property
    def platform(self) -> str:
        """Returns the platform of the browser"""
        return self.window.evaluate_js('navigator.platform') or ''
    
    @property
    def product(self) -> str:
        """Returns the product name of the browser"""
        return self.window.evaluate_js('navigator.product') or ''
    
    @property
    def userAgent(self) -> str:
        """Returns browser user-agent header"""
        return self.window.evaluate_js('navigator.userAgent') or ''
    
    def javaEnabled(self) -> bool:
        """Returns whether Java is enabled in the browser"""
        return self.window.evaluate_js('navigator.javaEnabled()') or False

class Screen:
    """Screen object for screen information"""
    def __init__(self, window):
        self.window = window
    
    @property
    def availHeight(self) -> int:
        """Returns the height of the screen (excluding the Windows Taskbar)"""
        return self.window.evaluate_js('screen.availHeight') or 0
    
    @property
    def availWidth(self) -> int:
        """Returns the width of the screen (excluding the Windows Taskbar)"""
        return self.window.evaluate_js('screen.availWidth') or 0
    
    @property
    def colorDepth(self) -> int:
        """Returns the bit depth of the color palette for displaying images"""
        return self.window.evaluate_js('screen.colorDepth') or 0
    
    @property
    def height(self) -> int:
        """Returns the total height of the screen"""
        return self.window.evaluate_js('screen.height') or 0
    
    @property
    def pixelDepth(self) -> int:
        """Returns the color resolution (in bits per pixel) of the screen"""
        return self.window.evaluate_js('screen.pixelDepth') or 0
    
    @property
    def width(self) -> int:
        """Returns the total width of the screen"""
        return self.window.evaluate_js('screen.width') or 0

class HTMLWindow:
    """HTML Window object providing JavaScript window functionality"""
    def __init__(self, window):
        self.window = window
        self._console = Console(window)
        self._history = History(window)
        self._location = Location(window)
        self._navigator = Navigator(window)
        self._screen = Screen(window)
    
    # Properties
    @property
    def closed(self) -> bool:
        """Returns a boolean true if a window is closed"""
        return self.window.evaluate_js('window.closed') or False
    
    @property
    def console(self) -> Console:
        """Returns the Console Object for the window"""
        return self._console
    
    @property
    def document(self):
        """Returns the Document object for the window"""
        return Document(self.window)
    
    @property
    def frameElement(self):
        """Returns the frame in which the window runs"""
        return self.window.evaluate_js('window.frameElement')
    
    @property
    def frames(self):
        """Returns all window objects running in the window"""
        return self.window.evaluate_js('window.frames')
    
    @property
    def history(self) -> History:
        """Returns the History object for the window"""
        return self._history
    
    @property
    def innerHeight(self) -> int:
        """Returns the height of the window's content area (viewport) including scrollbars"""
        return self.window.evaluate_js('window.innerHeight') or 0
    
    @property
    def innerWidth(self) -> int:
        """Returns the width of a window's content area (viewport) including scrollbars"""
        return self.window.evaluate_js('window.innerWidth') or 0
    
    @property
    def length(self) -> int:
        """Returns the number of <iframe> elements in the current window"""
        return self.window.evaluate_js('window.length') or 0
    
    @property
    def localStorage(self):
        """Allows to save key/value pairs in a web browser. Stores the data with no expiration date"""
        return self.window.evaluate_js('window.localStorage')
    
    @property
    def location(self) -> Location:
        """Returns the Location object for the window"""
        return self._location
    
    @property
    def name(self) -> str:
        """Sets or returns the name of a window"""
        return self.window.evaluate_js('window.name') or ''
    
    @name.setter
    def name(self, value: str):
        """Sets the name of a window"""
        self.window.evaluate_js(f'window.name = {json.dumps(value)}')
    
    @property
    def navigator(self) -> Navigator:
        """Returns the Navigator object for the window"""
        return self._navigator
    
    @property
    def opener(self):
        """Returns a reference to the window that created the window"""
        return self.window.evaluate_js('window.opener')
    
    @property
    def outerHeight(self) -> int:
        """Returns the height of the browser window, including toolbars/scrollbars"""
        return self.window.evaluate_js('window.outerHeight') or 0
    
    @property
    def outerWidth(self) -> int:
        """Returns the width of the browser window, including toolbars/scrollbars"""
        return self.window.evaluate_js('window.outerWidth') or 0
    
    @property
    def pageXOffset(self) -> int:
        """Returns the pixels the current document has been scrolled (horizontally) from the upper left corner of the window"""
        return self.window.evaluate_js('window.pageXOffset') or 0
    
    @property
    def pageYOffset(self) -> int:
        """Returns the pixels the current document has been scrolled (vertically) from the upper left corner of the window"""
        return self.window.evaluate_js('window.pageYOffset') or 0
    
    @property
    def parent(self):
        """Returns the parent window of the current window"""
        return self.window.evaluate_js('window.parent')
    
    @property
    def screen(self) -> Screen:
        """Returns the Screen object for the window"""
        return self._screen
    
    @property
    def screenLeft(self) -> int:
        """Returns the horizontal coordinate of the window relative to the screen"""
        return self.window.evaluate_js('window.screenLeft') or 0
    
    @property
    def screenTop(self) -> int:
        """Returns the vertical coordinate of the window relative to the screen"""
        return self.window.evaluate_js('window.screenTop') or 0
    
    @property
    def screenX(self) -> int:
        """Returns the horizontal coordinate of the window relative to the screen"""
        return self.window.evaluate_js('window.screenX') or 0
    
    @property
    def screenY(self) -> int:
        """Returns the vertical coordinate of the window relative to the screen"""
        return self.window.evaluate_js('window.screenY') or 0
    
    @property
    def sessionStorage(self):
        """Allows to save key/value pairs in a web browser. Stores the data for one session"""
        return self.window.evaluate_js('window.sessionStorage')
    
    @property
    def scrollX(self) -> int:
        """An alias of pageXOffset"""
        return self.pageXOffset
    
    @property
    def scrollY(self) -> int:
        """An alias of pageYOffset"""
        return self.pageYOffset
    
    @property
    def self(self):
        """Returns the current window"""
        return self
    
    @property
    def top(self):
        """Returns the topmost browser window"""
        return self.window.evaluate_js('window.top')
    
    # Methods
    def addEventListener(self, event_type: str, callback) -> bool:
        """Attaches an event handler to the window"""
        # Get the PyContext from the window
        context = None
        if hasattr(self.window, '_py_context'):
            context = self.window._py_context
        
        if not context:
            # If no context found, create a temporary one just for this handler
            context = PositronContext(self.window)
            self.window._py_context = context
            
        # Register the event handler with the context using 'window' as element_id
        handler_key = context.register_event_handler('window', event_type, callback)
        
        # Create global event handler if not already created
        if not hasattr(self.window, 'handle_py_event'):
            def handle_py_event(element_id, event_type):
                key = f"{element_id}_{event_type}"
                if hasattr(self.window, '_py_context') and key in self.window._py_context.event_handlers:
                    try:
                        return self.window._py_context.event_handlers[key]()
                    except Exception as e:
                        print(f"[ERROR] handling event: {e}")
                        traceback.print_exc()
                        return str(e)
                print(f"WARNING: No handler found for {key}")
                return False
                
            self.window.handle_py_event = handle_py_event
            self.window.expose(handle_py_event)
        
        # Add the event listener in JavaScript
        js_code = f"""
        window.addEventListener("{event_type}", function(event) {{
            console.log("Window event triggered: {event_type}");
            window.pywebview.api.handle_py_event("window", "{event_type}");
        }});
        """
        
        success = self.window.evaluate_js(js_code)
        return success
    
    def alert(self, message: str):
        """Displays an alert box with a message and an OK button"""
        self.window.evaluate_js(f'alert({json.dumps(message)})')
    
    def atob(self, encoded_string: str) -> str:
        """Decodes a base-64 encoded string"""
        return self.window.evaluate_js(f'atob({json.dumps(encoded_string)})')
    
    def blur(self):
        """Removes focus from the current window"""
        self.window.evaluate_js('window.blur()')
    
    def btoa(self, string: str) -> str:
        """Encodes a string in base-64"""
        return self.window.evaluate_js(f'btoa({json.dumps(string)})')
    
    def clearInterval(self, interval_id: int):
        """Clears a timer set with setInterval()"""
        self.window.evaluate_js(f'clearInterval({interval_id})')
    
    def clearTimeout(self, timeout_id: int):
        """Clears a timer set with setTimeout()"""
        self.window.evaluate_js(f'clearTimeout({timeout_id})')
    
    def close(self):
        """Closes the current window"""
        self.window.evaluate_js('window.close()')
    
    def confirm(self, message: str) -> bool:
        """Displays a dialog box with a message and an OK and a Cancel button"""
        return self.window.evaluate_js(f'confirm({json.dumps(message)})')
    
    def focus(self):
        """Sets focus to the current window"""
        self.window.evaluate_js('window.focus()')
    
    def getComputedStyle(self, element, pseudo_element=None):
        """Gets the current computed CSS styles applied to an element"""
        if isinstance(element, Element):
            if pseudo_element:
                return self.window.evaluate_js(f'getComputedStyle({element.js_path}, {json.dumps(pseudo_element)})')
            else:
                return self.window.evaluate_js(f'getComputedStyle({element.js_path})')
        else:
            raise TypeError("getComputedStyle expects an Element")
    
    def getSelection(self):
        """Returns a Selection object representing the range of text selected by the user"""
        return self.window.evaluate_js('window.getSelection()')
    
    def matchMedia(self, media_query: str):
        """Returns a MediaQueryList object representing the specified CSS media query string"""
        return self.window.evaluate_js(f'window.matchMedia({json.dumps(media_query)})')
    
    def moveBy(self, x: int, y: int):
        """Moves a window relative to its current position"""
        self.window.evaluate_js(f'window.moveBy({x}, {y})')
    
    def moveTo(self, x: int, y: int):
        """Moves a window to the specified position"""
        self.window.evaluate_js(f'window.moveTo({x}, {y})')
    
    def open(self, url: str = '', name: str = '_blank', specs: str = '', replace: bool = False):
        """Opens a new browser window"""
        return self.window.evaluate_js(f'window.open({json.dumps(url)}, {json.dumps(name)}, {json.dumps(specs)}, {json.dumps(replace)})')
    
    def print(self):
        """Prints the content of the current window"""
        self.window.evaluate_js('window.print()')
    
    def prompt(self, message: str, default_value: str = '') -> str:
        """Displays a dialog box that prompts the visitor for input"""
        return self.window.evaluate_js(f'prompt({json.dumps(message)}, {json.dumps(default_value)})')
    
    def removeEventListener(self, event_type: str, callback=None):
        """Removes an event handler from the window"""
        # For simplicity, we'll remove all handlers for this event type on window
        if hasattr(self.window, '_py_context'):
            key = f"window_{event_type}"
            if key in self.window._py_context.event_handlers:
                del self.window._py_context.event_handlers[key]
        
        js_code = f"""
        // Note: This is a simplified implementation
        console.log("removeEventListener called for {event_type} on window");
        """
        self.window.evaluate_js(js_code)
    
    def requestAnimationFrame(self, callback):
        """Requests the browser to call a function to update an animation before the next repaint"""
        # This is complex to implement with Python callbacks, simplified version
        self.window.evaluate_js('requestAnimationFrame(function() { console.log("Animation frame requested"); })')
        return 1  # Return a dummy request id
    
    def resizeBy(self, width: int, height: int):
        """Resizes the window by the specified pixels"""
        self.window.evaluate_js(f'window.resizeBy({width}, {height})')
    
    def resizeTo(self, width: int, height: int):
        """Resizes the window to the specified width and height"""
        self.window.evaluate_js(f'window.resizeTo({width}, {height})')
    
    def scrollBy(self, x: int, y: int):
        """Scrolls the document by the specified number of pixels"""
        self.window.evaluate_js(f'window.scrollBy({x}, {y})')
    
    def scrollTo(self, x: int, y: int):
        """Scrolls the document to the specified coordinates"""
        self.window.evaluate_js(f'window.scrollTo({x}, {y})')
    
    def setInterval(self, callback, milliseconds: int) -> int:
        """Calls a function or evaluates an expression at specified intervals (in milliseconds)"""
        # This is complex to implement with Python callbacks, simplified version
        interval_id = self.window.evaluate_js(f'setInterval(function() {{ console.log("Interval callback"); }}, {milliseconds})')
        return interval_id or 1  # Return interval id
    
    def setTimeout(self, callback, milliseconds: int) -> int:
        """Calls a function or evaluates an expression after a specified number of milliseconds"""
        # This is complex to implement with Python callbacks, simplified version
        timeout_id = self.window.evaluate_js(f'setTimeout(function() {{ console.log("Timeout callback"); }}, {milliseconds})')
        return timeout_id or 1  # Return timeout id
    
    def stop(self):
        """Stops the window from loading"""
        self.window.evaluate_js('window.stop()')

class Document:
    def __init__(self, window):
        self.window = window
    
    # Properties
    @property
    def activeElement(self) -> Element:
        """Returns the currently focused element in the document"""
        return Element(self.window, 'document.activeElement')
    
    @property
    def baseURI(self) -> str:
        """Returns the absolute base URI of a document"""
        return self.window.evaluate_js('document.baseURI')
    
    @property
    def characterSet(self) -> str:
        """Returns the character encoding for the document"""
        return self.window.evaluate_js('document.characterSet')
    
    @property
    def cookie(self) -> str:
        """Returns all name/value pairs of cookies in the document"""
        return self.window.evaluate_js('document.cookie')
    
    @cookie.setter
    def cookie(self, value: str):
        """Sets cookies in the document"""
        self.window.evaluate_js(f'document.cookie = {json.dumps(value)}')
    
    @property
    def defaultView(self):
        """Returns the window object associated with a document, or null if none is available"""
        return self.window.evaluate_js('document.defaultView')
    
    @property
    def designMode(self) -> str:
        """Controls whether the entire document should be editable or not"""
        return self.window.evaluate_js('document.designMode')
    
    @designMode.setter
    def designMode(self, value: str):
        """Sets whether the entire document should be editable or not"""
        self.window.evaluate_js(f'document.designMode = {json.dumps(value)}')
    
    @property
    def doctype(self):
        """Returns the Document Type Declaration associated with the document"""
        return self.window.evaluate_js('document.doctype')
    
    @property
    def documentElement(self) -> Element:
        """Returns the Document Element of the document (the <html> element)"""
        return Element(self.window, 'document.documentElement')
    
    @property
    def documentURI(self) -> str:
        """Returns the location of the document"""
        return self.window.evaluate_js('document.documentURI')
    
    @property
    def domain(self) -> str:
        """Returns the domain name of the server that loaded the document"""
        return self.window.evaluate_js('document.domain')
    
    @property
    def embeds(self) -> ElementList:
        """Returns a collection of all <embed> elements the document"""
        return ElementList(self.window, 'document.embeds')
    
    @property
    def head(self) -> Element:
        """Returns the <head> element of the document"""
        return Element(self.window, 'document.head')
    
    @property
    def images(self) -> ElementList:
        """Returns a collection of all <img> elements in the document"""
        return ElementList(self.window, 'document.images')
    
    @property
    def implementation(self):
        """Returns the DOMImplementation object that handles this document"""
        return self.window.evaluate_js('document.implementation')
    
    @property
    def lastModified(self) -> str:
        """Returns the date and time the document was last modified"""
        return self.window.evaluate_js('document.lastModified')
    
    @property
    def links(self) -> ElementList:
        """Returns a collection of all <a> and <area> elements in the document that have a href attribute"""
        return ElementList(self.window, 'document.links')
    
    @property
    def readyState(self) -> str:
        """Returns the (loading) status of the document"""
        return self.window.evaluate_js('document.readyState')
    
    @property
    def referrer(self) -> str:
        """Returns the URL of the document that loaded the current document"""
        return self.window.evaluate_js('document.referrer')
    
    @property
    def scripts(self) -> ElementList:
        """Returns a collection of <script> elements in the document"""
        return ElementList(self.window, 'document.scripts')
    
    @property
    def title(self) -> str:
        """Returns the title of the document"""
        return self.window.evaluate_js('document.title')
    
    @title.setter
    def title(self, value: str):
        """Sets the title of the document"""
        self.window.evaluate_js(f'document.title = {json.dumps(value)}')
    
    @property
    def URL(self) -> str:
        """Returns the full URL of the HTML document"""
        return self.window.evaluate_js('document.URL')
    
    # Methods
    def addEventListener(self, event_type: str, callback) -> bool:
        """Attaches an event handler to the document"""
        # Get the PyContext from the window
        context = None
        if hasattr(self.window, '_py_context'):
            context = self.window._py_context
        
        if not context:
            # If no context found, create a temporary one just for this handler
            context = PositronContext(self.window)
            self.window._py_context = context
            
        # Register the event handler with the context using 'document' as element_id
        handler_key = context.register_event_handler('document', event_type, callback)
        
        # Create global event handler if not already created
        if not hasattr(self.window, 'handle_py_event'):
            def handle_py_event(element_id, event_type):
                key = f"{element_id}_{event_type}"
                if hasattr(self.window, '_py_context') and key in self.window._py_context.event_handlers:
                    try:
                        return self.window._py_context.event_handlers[key]()
                    except Exception as e:
                        print(f"[ERROR] handling event: {e}")
                        traceback.print_exc()
                        return str(e)
                print(f"WARNING: No handler found for {key}")
                return False
                
            self.window.handle_py_event = handle_py_event
            self.window.expose(handle_py_event)
        
        # Add the event listener in JavaScript
        js_code = f"""
        document.addEventListener("{event_type}", function(event) {{
            console.log("Document event triggered: {event_type}");
            window.pywebview.api.handle_py_event("document", "{event_type}");        }});
        """
        
        success = self.window.evaluate_js(js_code)
        return success
    
    def adoptNode(self, node):
        """Adopts a node from another document"""
        if isinstance(node, Element):
            return Element(self.window, f'document.adoptNode({node.js_path})')
        else:
            raise TypeError("adoptNode expects an Element")
    
    def close(self):
        """Closes the output stream previously opened with document.open()"""
        self.window.evaluate_js('document.close()')
    
    def createAttribute(self, name: str):
        """Creates an attribute node"""
        return self.window.evaluate_js(f'document.createAttribute({json.dumps(name)})')
    
    def createComment(self, text: str):
        """Creates a Comment node with the specified text"""
        return self.window.evaluate_js(f'document.createComment({json.dumps(text)})')
    
    def createDocumentFragment(self):
        """Creates an empty DocumentFragment node"""
        return self.window.evaluate_js('document.createDocumentFragment()')
    
    def createEvent(self, event_type: str):
        """Creates a new event"""
        return self.window.evaluate_js(f'document.createEvent({json.dumps(event_type)})')
    
    def createTextNode(self, text: str):
        """Creates a Text node"""
        return self.window.evaluate_js(f'document.createTextNode({json.dumps(text)})')
    
    def getElementsByName(self, name: str) -> ElementList:
        """Returns a live NodeList containing all elements with the specified name"""
        return ElementList(self.window, f'document.getElementsByName({json.dumps(name)})')
    
    def getElementsByTagName(self, tag_name: str) -> ElementList:
        """Returns an HTMLCollection containing all elements with the specified tag name"""
        return ElementList(self.window, f'document.getElementsByTagName({json.dumps(tag_name)})')
    
    def hasFocus(self) -> bool:
        """Returns a Boolean value indicating whether the document has focus"""
        return self.window.evaluate_js('document.hasFocus()')
    
    def importNode(self, node, deep: bool = False):
        """Imports a node from another document"""
        if isinstance(node, Element):
            return Element(self.window, f'document.importNode({node.js_path}, {json.dumps(deep)})')
        else:
            raise TypeError("importNode expects an Element")
    
    def normalize(self):
        """Removes empty Text nodes, and joins adjacent nodes"""
        self.window.evaluate_js('document.normalize()')
    
    def open(self, mime_type: str | None = None, replace: str | None = None):
        """Opens an HTML output stream to collect output from document.write()"""
        if mime_type and replace:
            return self.window.evaluate_js(f'document.open({json.dumps(mime_type)}, {json.dumps(replace)})')
        elif mime_type:
            return self.window.evaluate_js(f'document.open({json.dumps(mime_type)})')
        else:
            return self.window.evaluate_js('document.open()')
    
    def removeEventListener(self, event_type: str, callback=None):
        """Removes an event handler from the document"""
        # For simplicity, we'll remove all handlers for this event type on document
        if hasattr(self.window, '_py_context'):
            key = f"document_{event_type}"
            if key in self.window._py_context.event_handlers:
                del self.window._py_context.event_handlers[key]
        
        js_code = f"""
        // Note: This is a simplified implementation
        // In a real implementation, you'd need to track the specific handler function
        console.log("removeEventListener called for {event_type} on document");
        """
        self.window.evaluate_js(js_code)
    
    def write(self, *args):
        """Writes HTML expressions or JavaScript code to a document"""
        content = ''.join(str(arg) for arg in args)
        self.window.evaluate_js(f'document.write({json.dumps(content)})')
    
    def writeln(self, *args):
        """Same as write(), but adds a newline character after each statement"""
        content = ''.join(str(arg) for arg in args)
        self.window.evaluate_js(f'document.writeln({json.dumps(content)})')

    # Existing methods
    def getElementById(self, element_id) -> Element:
        """Get element by ID"""
        return Element(self.window, f'document.getElementById("{element_id}")')
    def getElementsByClassName(self, class_name) -> ElementList:
        """Get elements by class name"""
        return ElementList(self.window, f'document.getElementsByClassName("{class_name}")')
    def querySelector(self, selector) -> Element:
        """Query selector - Selects a single element from the DOM matching a CSS query selector."""
        return Element(self.window, f'document.querySelector("{selector}")')
    def querySelectorAll(self, selector) -> ElementList:
        """Query selector all - Selects all elements from the DOM matching a CSS query selector."""
        return ElementList(self.window, f'document.querySelectorAll("{selector}")')
    def createElement(self, tag_name) -> Element:
        """Create element"""
        return Element(self.window, f'document.createElement("{tag_name}")')
    def alert(self, message) -> None:
        """Show alert pop-up."""
        self.window.evaluate_js(f'alert("{escape_js_string(message)}")')
    def confirm(self, message) -> bool:
        """Show confirm dialog with "Yes" and "No" buttons, returns True or False."""
        return self.window.evaluate_js(f'confirm("{escape_js_string(message)}")')
    def prompt(self, message:str, default_value=None) -> str:
        """Show prompt dialog with an input field, returns the input value or None if cancelled."""
        if default_value:
            return self.window.evaluate_js(f'prompt("{(escape_js_string(message))}", "{escape_js_string(default_value)}")')
        return self.window.evaluate_js(f'prompt("{escape_js_string(message)}")')
    @property
    def body(self) -> Element:
        """Get body element"""
        return Element(self.window, 'document.body')
    @property
    def html(self) -> Element:
        """Get html element"""
        return Element(self.window, 'document.html')
    @property
    def forms(self) -> ElementList:
        """Get all the forms in a document"""
        return ElementList(self.window, 'document.forms')

    # Add switchView to reload a new HTML and re-execute its <py> tags
    def switchView(self, path: str) -> bool:
        """Switch to another HTML view and (re)execute its <py> tags."""
        ctx = getattr(self.window, '_py_context', None)
        if not ctx or not hasattr(ctx, 'switch_view'):
            raise RuntimeError("switch_view not available")
        return ctx.switch_view(path)

class ExposedFunctions:
    def __init__(self, functions_dict):
        for name, func in functions_dict.items():
            setattr(self, name, func)

def run_python_code_in_html(html_content, context):
    try:
        # Handle <py src="..."> tags
        src_pattern = re.compile(r'<py(?:\s*|\s.*\s)src=\"(.*?)\"\s?.*>.*</py>', re.DOTALL)
        for match in src_pattern.finditer(html_content):
            path = match.group(1)
            if not os.path.isabs(path):
                path = os.path.abspath(path)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    src_code = f.read()
            except Exception as e:
                print(f"[ERROR] loading Python src '{path}': {e}")
                continue
            try:
                success, error = context.execute(src_code)
                if success == False:
                    print(f"[ERROR] in <py src> tag code execution: {error}")
            except Exception as e:
                print(f"[ERROR] in <py src> tag execution function: {e}\n[NOTE] This error happened within the function for running the python code, not the code itself.\nIt may be a problem with PyPositron.")        # Handle <py> tags (without src)
        no_src_pattern = re.compile(r"<py(?:|\s.+)>(.*?)</py>", re.DOTALL)
        matches = list(no_src_pattern.finditer(html_content))
        for match in matches:
            code = match.group(1)
            # Decode HTML entities so users can include < and > as &lt; &gt;
            code = html.unescape(code)
            # Handle indented Python code in HTML more robustly
            # First strip leading/trailing whitespace
            code = code.strip()
            
            # Custom dedent logic to handle mixed indentation better
            if code:
                lines = code.split('\n')
                # Find minimum indentation (excluding empty lines and comments without code)
                non_empty_lines = [line for line in lines if (line.strip() and not line.strip().startswith('#'))]
                if non_empty_lines:
                    # Get indentation for each non-empty line
                    indentations = [len(line) - len(line.lstrip()) for line in non_empty_lines]
                    
                    # If minimum indentation is 0 (e.g., due to unindented comment), 
                    # find the most common indentation level among actual code lines
                    min_indent = min(indentations)
                    if min_indent == 0 and len(indentations) > 1:
                        # Filter out zero indentations and find the minimum of the rest
                        non_zero_indents = [i for i in indentations if i > 0]
                        if non_zero_indents:
                            min_indent = min(non_zero_indents)
                    
                    # Remove the minimum indentation from all lines
                    if min_indent > 0:
                        dedented_lines = []
                        for line in lines:
                            if line.strip():  # Non-empty line
                                if len(line) >= min_indent and line[:min_indent].isspace():
                                    dedented_lines.append(line[min_indent:])
                                else:
                                    dedented_lines.append(line.lstrip())
                            else:  # Empty line
                                dedented_lines.append('')
                        code = '\n'.join(dedented_lines)
            
            success, error = context.execute(code)
            if success == False:
                print(f"[ERROR] in <py> tag execution: {error}")
        return html_content
    except Exception as e:
        print(f"[ERROR] in processsing <py> tags: {e}")
        print(traceback.format_exc())
        return html_content

def openUI(html_path, main: Callable[[PositronWindowWrapper], None] | None = None, after_close: Callable[[PositronWindowWrapper], None] | None = None, width=900, height=700, title="Window", functions=None,
            x: int | None = None,
            y: int | None = None,
            resizable=True,
            fullscreen: bool = False,
            min_size: tuple[int, int] = (200, 100),
            hidden: bool = False,
            frameless: bool = False,
            easy_drag: bool = True,
            shadow: bool = True,
            focus: bool = True,
            minimized: bool = False,
            maximized: bool = False,
            on_top: bool = False,
            confirm_close: bool = False,
            background_color: str = '#FFFFFF',
            transparent: bool = False,
            text_select: bool = False,
            zoomable: bool = False,
            draggable: bool = False,
            vibrancy: bool = False,
            
            gui = None,
            debug: bool = False,
            http_server: bool = False,
            http_port: int | None = None,
            user_agent: str | None = None,
            private_mode: bool = True,
            storage_path: str | None = None,
            icon: str | None = None,
            ):
    """
    Open a UI window with the specified HTML file and run the main function in a background thread.
            Parameters:
            -----------
            html_path : str
                Path to the HTML file to load.
            main : function
                The main function to run in the background thread. It should accept a PositronWindow object.
            width : int, optional
                Width of the window. Default is 900.
            height : int, optional
                Height of the window. Default is 700.
            title : str, optional
                Title of the window. Default is "Python UI".
            functions : list, optional
                List of functions to expose to JavaScript.
            x : int, optional
                X coordinate of the window.
            y : int, optional
                Y coordinate of the window.
            resizable : bool, optional
                Whether the window is resizable. Default is True.
            fullscreen : bool, optional
                Whether the window is fullscreen. Default is False.
            min_size : tuple[int, int], optional
                Minimum size (width, height) of the window. Default is (200, 100).
            hidden : bool, optional
                Whether the window is initially hidden. Default is False.
            frameless : bool, optional
                Whether the window has no frame/border. Default is False.
            easy_drag : bool, optional
                Whether frameless windows can be easily dragged. Default is True.
            shadow : bool, optional
                Whether the window has a shadow. Default is True.
            focus : bool, optional
                Whether the window has focus when created. Default is True.
            minimized : bool, optional
                Whether the window is initially minimized. Default is False.
            maximized : bool, optional
                Whether the window is initially maximized. Default is False.
            on_top : bool, optional
                Whether the window stays on top of other windows. Default is False.
            confirm_close : bool, optional
                Whether to show a confirmation dialog when closing the window. Default is False.
            background_color : str, optional
                Background color of the window. Default is '#FFFFFF'.
            transparent : bool, optional
                Whether the window background is transparent. Default is False.
            text_select : bool, optional
                Whether text selection is enabled. Default is False.
            zoomable : bool, optional
                Whether the content can be zoomed. Default is False.
            draggable : bool, optional
                Whether the window can be dragged by the user. Default is False.
            vibrancy : bool, optional
                Whether the window has a vibrancy effect (macOS). Default is False.
            gui : webview.GUIType | None, optional
                GUI toolkit to use. Default is None (auto-select). Must be one of ['qt', 'gtk', 'cef', 'mshtml', 'edgechromium', 'android'].
            debug : bool, optional
                Whether to enable debug mode. Default is False.
            http_server : bool, optional
                Whether to serve local files using HTTP server. Default is False.
            http_port : int | None, optional
                HTTP server port. Default is None (auto-select).
            user_agent : str | None, optional
                Custom user agent string. Default is None.
            private_mode : bool, optional
                Whether to run in private browsing mode. Default is True.
            storage_path : str | None, optional
                Path for storing browser data. Default is None.
            icon : str | None, optional
                Path to the window icon. Default is None. Only supported in QT/GTK.
            Returns:
            --------
            PositronWindow
                A wrapper object that provides access to the window and context.
            Raises:
            -------
            RuntimeError
                If not called from the main thread.
            FileNotFoundError
                If the HTML file is not found.
    """
    if threading.current_thread().name != "MainThread":
        raise RuntimeError("openUI must be called from the main thread.")
    if not os.path.isabs(html_path):
        html_path = os.path.abspath(html_path)
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    # Remember directory for relative paths
    html_dir = os.path.dirname(html_path)
    if debug:
        print(f"[DEBUG] Loading HTML from: {html_path}")
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    window = webview.create_window(
        title=title,
        url=html_path,
        width=width,
        height=height,
        x=x,
        y=y,
        resizable=resizable,
        fullscreen=fullscreen,
        min_size=min_size,
        hidden=hidden,
        frameless=frameless,
        easy_drag=easy_drag,
        shadow=shadow,
        focus=focus,
        minimized=minimized,
        maximized=maximized,
        on_top=on_top,
        confirm_close=confirm_close,
        background_color=background_color,
        transparent=transparent,
        text_select=text_select,
        zoomable=zoomable,
        draggable=draggable,
        vibrancy=vibrancy,
    )

    context = PositronContext(window)
    window._py_context = context # type: ignore
    if functions:
        for func in functions:
            context.exposed_functions[func.__name__] = func
            window.expose(func)

    # Implement switch_view on context and expose to JS
    def switch_view(path):
        # resolve relative path
        if not os.path.isabs(path):
            abs_path = os.path.abspath(os.path.join(html_dir, path))
        else:
            abs_path = path
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"HTML file not found: {abs_path}")

        # load new content and run py-tags
        with open(abs_path, 'r', encoding='utf-8') as f:
            new_content = f.read()
        window.load_url(abs_path)
        run_python_code_in_html(new_content, context)
        return True

    context.switch_view = switch_view
    window.expose(switch_view)

    def process_py_tags():
        try:
            sys.stdout.flush()
            run_python_code_in_html(html_content, context)
            if functions:
                function_dict = {func.__name__: func for func in functions}
                js_code = """
                if (!window.python) {
                    window.python = {};
                }
                """
                for func_name in function_dict:
                    js_code += f"""
                    window.python.{func_name} = function() {{
                        return window.pywebview.api.{func_name}.apply(null, arguments);
                    }};
                    """
                window.evaluate_js(js_code)
            def debug_event_handlers():
                if hasattr(window, '_py_context'):
                    handlers = list(window._py_context.event_handlers.keys()) # type: ignore
                    return f"Registered handlers: {handlers}"
                return "No event handlers found"
            window.expose(debug_event_handlers)
        except Exception as e:
            print(f"[ERROR] in process_html thread: {e}")
            print(traceback.format_exc())
    # Run the main function in a separate thread if given.
    if main != None:
        def __main_wrapper():
            main(PositronWindowWrapper(window, context, threading.current_thread()))
        main_function_thread = threading.Thread(target=__main_wrapper, daemon=True)
        main_function_thread.start()
    # Start processing <py> tags in background
    process_thread = threading.Thread(target=process_py_tags, daemon=True)
    process_thread.start()
    # Launch the webview event loop.
    webview.start(
        gui=gui,
        debug=debug,
        http_server=http_server,
        http_port=http_port,
        user_agent=user_agent,
        private_mode=private_mode,
        storage_path=storage_path,
        icon=icon,
    )
    # Call the afterclose function if provided
    if after_close != None:
        def __after_close_wrapper():
            after_close(PositronWindowWrapper(window, context, threading.current_thread()))
        after_close_thread = threading.Thread(target=__after_close_wrapper, daemon=True)
        after_close_thread.start()
    return PositronWindowWrapper(window, context, threading.current_thread())

def start():
    """Start the webview event loop."""
    webview.start()


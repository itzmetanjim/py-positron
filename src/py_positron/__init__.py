__version__ = "0.0.2.1" 
import webview
import os
import threading
import re
import importlib
import json
import traceback
import sys
import html
from typing import Callable
class PositronWindowWrapper:
    """Wrapper for a PyPositron window with event loop thread and context."""
    def __init__(self, window, context, main_thread):
        self.window: webview.Window = window
        self.context: PositronContext = context
        self.document = Document(window)
        self.exposed = ExposedFunctions(context.exposed_functions)
        self.event_thread: threading.Thread = main_thread

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
    
    def setAttribute(self, attr_name, value):
        """Set attribute"""
        self.window.evaluate_js(f'{self.js_path}.setAttribute("{attr_name}", {json.dumps(value)})')
    
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

class Document:
    def __init__(self, window):
        self.window = window
        #self.readyState
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
            x:int=None,
            y:int=None,
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
            
            gui: webview.GUIType | None = None,
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
    window._py_context = context
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
                    handlers = list(window._py_context.event_handlers.keys())
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



"""
Contains the base class for loading a 32-bit shared library in 32-bit Python.

The :class:`~.server32.Server32` class is used in combination with the
:class:`~.client64.Client64` class to communicate with a 32-bit shared library
from 64-bit Python.
"""

# # Importing file with setting that lets us know if a current build is active
# import current_build_settings

import os
import re
import sys
import json
import traceback
import threading
import subprocess
try:
    import cPickle as pickle  # Python 2
except ImportError:
    import pickle
try:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler  # Python 2
except ImportError:
    from http.server import HTTPServer, BaseHTTPRequestHandler

from loadlib import LoadLibrary, SERVER_FILENAME, IS_WINDOWS

METADATA = '-METADATA-'
SHUTDOWN = '-SHUTDOWN-'
OK = 200
ERROR = 500


#*** Random String Generator ***
# Allows us to get a random string to use as the encryption key every time
import random
import string

#Function to get random string to use as encryption key
#Returns a string of N length; containing ASCII uppercase letters, ASCII lower case letters, and numbers
def get_random_string(string_length=16):
    random_string = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(string_length))
    return str(random_string)

###############################################################################

#*** During a build, we include the DAQDevice Subclass ***

CODE_BUILD_IN_PROGRESS = False

# If a code build is active, then a current_build_setting.py file will exists
try:
    # Importing file with setting that lets us know if a current build is active
    import current_build_settings
    CODE_BUILD_IN_PROGRESS = current_build_settings.CODE_BUILD_ACTIVE
except:
    CODE_BUILD_IN_PROGRESS = False

# MagicDAQ code will be contained within the executable
# Making easydaq.DAQDevice a sub class of Server32 class to accomplish this
if CODE_BUILD_IN_PROGRESS:
    import easydaq


###############################################################################

# Declare Server32 class
class Server32(HTTPServer):

    def __init__(self, path, libtype, host, port, quiet, **kwargs):
        """Base class for loading a 32-bit library in 32-bit Python.

        All modules that are to be run on the 32-bit server must contain a class
        that is inherited from this class and the module can import **any** of
        the `standard`_ python modules **except** for :mod:`distutils`,
        :mod:`ensurepip`, :mod:`tkinter` and :mod:`turtle`.

        All modules that are run on the 32-bit server must be able to run on the Python
        interpreter that the server is running on, see :meth:`.version` for how to
        determine the version of the Python interpreter.

        .. _standard: https://docs.python.org/3/py-modindex.html
        .. _JVM: https://en.wikipedia.org/wiki/Java_virtual_machine

        Parameters
        ----------
        path : :class:`str`
            The path to the 32-bit library.
        libtype : :class:`str`
            The library type to use for the calling convention. One of the following:

                * ``'cdll'`` -- for a __cdecl library
                * ``'windll'`` or ``'oledll'`` -- for a __stdcall library (Windows only)
                * ``'net'`` or ``'clr'`` -- for Microsoft's .NET Framework (Common Language Runtime)
                * ``'com'`` -- for a `COM <https://en.wikipedia.org/wiki/Component_Object_Model>`_ library.

            .. note::
               Since Java byte code is executed on the JVM_ it does not make sense to
               use :class:`Server32` for a Java ``.jar`` or ``.class`` file.

        host : :class:`str`
            The IP address of the server.
        port : :class:`int`
            The port to open on the server.
        quiet : :class:`bool`
            Whether to hide :data:`sys.stdout` messages on the server.
        **kwargs
            Keyword arguments that are passed to :class:`.LoadLibrary`.

        Raises
        ------
        IOError
            If the shared library cannot be loaded.
        TypeError
            If the value of `libtype` is not supported.
        """
        self._quiet = bool(quiet)
        self._library = LoadLibrary(path, libtype=libtype, **kwargs)

        super(Server32, self).__init__((host, int(port)), _RequestHandler)

        # #We need to run the __init__() function for DAQDevice
        # easydaq.DAQDevice.__init__(self)

        # Original working code
        #We need to run the __init__() function for easydaq.DAQDevice
        #sub_class.__init__(self)

        #print('Server32 () INSTANTIATION function run!')


    @property
    def assembly(self):
        """
        Returns a reference to the `.NET Runtime Assembly <NET_>`_ object, *only if
        the shared library is a .NET Framework*, otherwise returns :data:`None`.

        .. tip::
           The `JetBrains dotPeek`_ program can be used to reliably decompile any
           .NET Assembly in to the equivalent source code.

        .. _NET: https://msdn.microsoft.com/en-us/library/system.reflection.assembly(v=vs.110).aspx
        .. _JetBrains dotPeek: https://www.jetbrains.com/decompiler/
        """
        return self._library.assembly

    @property
    def lib(self):
        """Returns the reference to the 32-bit, loaded library object.

        For example, if `libtype` is

        * ``'cdll'`` then a :class:`~ctypes.CDLL` object
        * ``'windll'`` then a :class:`~ctypes.WinDLL` object
        * ``'oledll'`` then a :class:`~ctypes.OleDLL` object
        * ``'net'`` or ``'clr'`` then a :class:`~.load_library.DotNet` object
        * ``'com'`` then the interface pointer returned by comtypes.CreateObject_

        .. _comtypes.CreateObject: https://pythonhosted.org/comtypes/#creating-and-accessing-com-objects
        """
        return self._library.lib

    @property
    def path(self):
        """:class:`str`: The path to the shared library file."""
        return self._library.path

    @staticmethod
    def version():
        """Gets the version of the Python interpreter that the 32-bit server is running on.

        Returns
        -------
        :class:`str`
            The result of executing ``'Python ' + sys.version`` on the 32-bit server.

        Examples
        --------
        ::

            #>>> from msl.loadlib import Server32
            #>>> Server32.version()  # doctest: +SKIP
            'Python 3.7.3 (v3.7.3:ef4ec6ed12, Mar 25 2019, 21:26:53) [MSC v.1916 32 bit (Intel)]'

        Note
        ----
        This method takes about 1 second to finish because the 32-bit server
        needs to start in order to determine the version of the Python interpreter.
        """
        exe = os.path.join(os.path.dirname(__file__), SERVER_FILENAME)
        pipe = subprocess.Popen([exe, '--version'], stdout=subprocess.PIPE)
        return pipe.communicate()[0].decode().strip()

    @staticmethod
    def interactive_console():
        """Start an interactive console.

        This method starts an interactive console, in a new terminal, with the
        Python interpreter on the 32-bit server.

        Examples
        --------
        ::

            #>>> from msl.loadlib import Server32
            #>>> Server32.interactive_console()  # doctest: +SKIP
        """
        exe = os.path.join(os.path.dirname(__file__), SERVER_FILENAME)
        if IS_WINDOWS:
            cmd = 'start "msl.loadlib.Server32 || interactive console" "{exe}" --interactive'
        else:
            cmd = "gnome-terminal --command='{exe} --interactive'"
        os.system(cmd.format(exe=exe))

    @property
    def quiet(self):
        """:class:`bool`: Whether :data:`sys.stdout` messages are hidden on the server."""
        return self._quiet

    def shutdown_handler(self):
        """
        Proxy function that is called immediately prior to the server shutting down.

        The intended use case is for the server to do any necessary cleanup, such as stopping
        locally started threads, closing file-handles, etc...

        .. versionadded:: 0.6
        """
        pass

# This is a global list of all daq objects
# format: [[ easydaq.DAQDevice object, unique_daq_id]]
daq_objects_list = []

class _RequestHandler(BaseHTTPRequestHandler):
    """Handles a request that was sent to the 32-bit server."""

    def do_GET(self):
        """Handle a GET request."""

        try:

            # Just in case response does not get set anywhere else
            response = None

            if self.path == METADATA:
                response = {'path': self.server.path, 'pid': os.getpid()}

            else:
                with open(self.server.pickle_path, 'rb') as f:
                    args = pickle.load(f)
                    kwargs = pickle.load(f)

                # 64bit client has instructed this 32bit server to instantiate a DAQ object
                if self.path == 'instantiate_daq_object':
                    global daq_objects_list
                    daq_objects_list.append([easydaq.DAQDevice(), args[0]])

                    # Default response is None
                    response = None

                # 64bit client instructing 32bit server to call a method on an object
                else:
                    matching_daq_id_found = False

                    # Find the correct daq object, and call the method
                    for daq_element in daq_objects_list:
                        # Check if the unique_daq_id matches
                        if args[0] == daq_element[1]:
                            # Call the method on the DAQ object
                            # Slice off the first argument (*args[1:]), we don't want to pass unique_daq_id to the MagicDAQ method
                            response = getattr(daq_element[0], self.path)(*args[1:], **kwargs)
                            matching_daq_id_found = True
                            break

                    # Check if an error has occurred
                    if not matching_daq_id_found:
                        print('ERROR: 32bit server unable to find matching unique_daq_id to apply method to.')
                        print('ERROR details: method: ',self.path, 'args: ',*args)
                        response = None

                    # Original code (before adding support for 2 DAQs at same time)
                    # This line effectively calls the self.path method name on the self.server object
                    # response = getattr(self.server, self.path)(*args, **kwargs)
                    # print('This is response: ', response)

            with open(self.server.pickle_path, 'wb') as f:

                # Apparently this line fails if the MagicDAQ driver is not installed.
                try:

                    pickle.dump(response, f, protocol=self.server.pickle_protocol)

                except Exception as exception_text:

                    # Very likely that the MagicDAQ Driver is not installed properly
                    no_driver_error_text = 'Original Exception: '
                    no_driver_error_text += str(exception_text) + '\n'
                    no_driver_error_text += 'MagicDAQ Driver NOT INSTALLED PROPERLY. '+'\n'
                    no_driver_error_text += 'Please see Install MagicDAQ in the MagicDAQ Docs. '+'\n'
                    no_driver_error_text += 'MagicDAQ Docs: https://magicdaq.github.io/magicdaq_docs/ '+'\n'
                    no_driver_error_text += 'You can email support at: support@magicdaq.com '+'\n'
                    raise Exception(str(no_driver_error_text))

            self.send_response(OK)
            self.end_headers()

        except Exception as e:
            print('{}: {}'.format(e.__class__.__name__, e))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_list = traceback.extract_tb(exc_traceback)
            tb = tb_list[min(len(tb_list)-1, 1)]  # get the Server32 subclass exception
            response = {'name': exc_type.__name__, 'value': str(exc_value)}
            traceback_ = '  File {!r}, line {}, in {}'.format(tb[0], tb[1], tb[2])
            if tb[3]:
                traceback_ += '\n    {}'.format(tb[3])
            response['traceback'] = traceback_
            self.send_response(ERROR)
            self.end_headers()
            self.wfile.write(json.dumps(response).encode(encoding='utf-8', errors='ignore'))

    def do_POST(self):
        """Handle a POST request."""
        if self.path == SHUTDOWN:
            self.server.shutdown_handler()
            threading.Thread(target=self.server.shutdown).start()
        else:  # the pickle info
            match = re.match(r'protocol=(\d+)&path=(.*)', self.path)
            if match:
                self.server.pickle_protocol = int(match.group(1))
                self.server.pickle_path = match.group(2)
                code = OK
            else:
                code = ERROR
            self.send_response(code)
            self.end_headers()

    def log_message(self, fmt, *args):
        """
        Overrides: :meth:`~http.server.BaseHTTPRequestHandler.log_message`

        Ignore all log messages from being displayed in :data:`sys.stdout`.
        """
        pass

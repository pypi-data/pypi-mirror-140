"""
Description of module
"""
from __future__ import annotations
import locale
import os
import shutil
import time
from tempfile import gettempdir
from typing import (Any, Dict, Generator, Iterator, KeysView, List,
                    MutableMapping, MutableSequence, Optional, Final, Tuple)
from xml.etree.ElementTree import Element, ElementTree

import requests
import win32com.client as win32
from pythoncom import com_error # type: ignore


class Player:
    """ Description of Player """

    ERROR_CODES: Final[Dict[str, int]] = {
        'software_error': 1010,
        'software_warn': 1000,
        'data_error': 1012,
        'data_warn': 1000
    }

    LANGUAGES: Final[Dict[str, int]] = {
        'EN': 0,
        'NL': 1
    }
    _prog_id_scalaplayer = 'ScalaPlayer.ScalaPlayer.1'
    _prog_id_filelock = 'ScalaFileLock.ScalaFileLock.1'
    _prog_id_infoplayer5 = 'Scala.InfoPlayer5'
    _prog_id_netic = 'Scala.InfoNetwork'

    _debug_field = 'Player.debug_python'
    _language_field = 'Player.language'
    _fi_api_field = 'Player.fi_api_key'
    _player_uuid_field = 'Player.uuid'

    _find_me_filename = 'find_me.txt'
    _find_me_path = os.path.join(gettempdir(), _find_me_filename)

    def __init__(self, script: str, main: bool = False) -> None:
        """
        The __init__ function is the constructor for a class. It is called whenever an instance of a class is created.
        The __init__ function can take arguments, but self is always the first one. Self refers to the instance being created;
        it's not a keyword, it's just a variable name (which happens to be "self"). The __init__ function doesn't return anything;
        it only modifies an existing object.

        :param self: Used to refer to the instance of the class.
        :param script:str: Used to set the script to be run.
        :param main:bool=False: Used to determine if the class is run from main.
        :return: None.

        :doc-author: Trelent
        """

        self._script = script
        self.is_main = main
        self.temp_folder = os.path.join(gettempdir(), self._script)

        if not self.is_main:
            self._scalaplayer = win32.Dispatch(self._prog_id_scalaplayer) # type: ignore
            self._netic = win32.Dispatch(self._prog_id_netic) # type: ignore
        else:
            print('This class is run from main. Because of this script will sent messages of whats its doing instead of doing it.')

        self._create_find_me()
        virtual_path = self.install_content(self._find_me_path)

        self.content_folder = os.path.dirname(
            str(self.find_content(virtual_path)))

        self.is_debug = self._get_debug()
        self.language = self._get_language()
        self.fi_api_key = self._get_fi_key()
        self.uuid = self._get_player_uuid()
        self._change_language()

        self.variables = self.Variables(self)

    def log(self, code: str, message: str) -> None:
        """
        The log function is used to log errors and warnings.

        :param self: Used to access the class instance itself.
        :param code:str: Used to identify the error.
        :param message:str: Used to pass a message to the log function.
        :return: None.

        :doc-author: Trelent
        """

        if not self.is_main:
            if code in self.ERROR_CODES.keys():
                self._scalaplayer.LogExternalError(self.ERROR_CODES[code], self._script, message) # type: ignore
            else:
                self._scalaplayer.Log('{} - {} - {}'.format(code, self._script, message)) # type: ignore
        else:
            print('{} - {} - {}'.format(code, self._script, message))

    def debug(self, msg: str) -> None:
        """
        The debug function prints a message if the is_debug attribute is True.

        :param self: Used to access the instance variables of the class.
        :param msg:str: Used to print the message to the console.
        :return: None.

        :doc-author: Trelent
        """

        if self.is_debug:
            self.log('DEBUG', msg)

    def error(self, msg: str, data: bool = False) -> None:
        """
        The error function is used to log errors in the software.
        It takes two arguments: a string describing the error, and a boolean indicating whether or not data was lost as a result of the error.

        :param self: Used to access the instance of the class.
        :param msg:str: Used to identify the error.
        :param data:bool=False: Used to tell the error function that this is a software error, not a data error.
        :return: None.

        :doc-author: Trelent
        """

        if data:
            self.log('data_error', msg)
        else:
            self.log('software_error', msg)

        raise SystemExit

    def warn(self, msg: str, data: bool = False) -> None:
        """
        The warn function is used to log warnings.

        :param self: Used to refer to the object that is calling the function.
        :param msg:str: Used to display the message to the user.
        :param data:bool=False: Used to tell the error function that this is a software error, not a data error.
        :return: None.

        :doc-author: Trelent
        """

        if data:
            self.log('data_warn', msg)
        else:
            self.log('software_warn', msg)

    def set_debug(self, value: bool):
        """
        The set_debug function sets the debug attribute of the class to True or False.

        :param self: Used to refer to the instance of the class.
        :param value:bool: Used to set the debug value.
        :return: None.

        :doc-author: Trelent
        """

        self.is_debug = value

    def set_variables(self, variables: Dict[str, Any]) -> None:
        """
        The set_variables function is used to set the variables dictionary for a
        sub-process. This is necessary because sub-processes cannot access the main
        process' variables dictionary, so they must be passed in explicitly.

        :param self: Used to access the current instance of the class.
        :param variables:Dict[str: Used to store the variables that are.
        :param Any]: Used to make the function call compatible with both.
        :return: None.

        :doc-author: Trelent
        """

        if self.is_main:
            self.variables = variables
        else:
            self.warn(
                'Setting the variables only possible when running python script from main')

    def set_language(self, language: str) -> None:
        """
        The set_language function sets the language of the class instance to a specified value.
           The function takes one argument, which is a string containing the name of any supported
           language.

        :param self: Used to access the instance variables of the class.
        :param language:str: Used to set the language of the user.
        :return: None.

        :doc-author: Trelent
        """

        self.language = self.LANGUAGES[language]
        self._change_language()

    def quit(self):
        """
        The quit function closes the InfoPlayer5 application.

        :param self: Used to refer to the object that is calling the function.
        :return: None.

        :doc-author: Trelent
        """

        if not self.is_main:
            win32.Dispatch(self._prog_id_infoplayer5).Quit() # type: ignore
        else:
            print('Quiting infoplayer')

    def restart(self):
        """
        The restart function restarts the playback of a video.

        :param self: Used to refer to the instance of the class.
        :return: nothing.

        :doc-author: Trelent
        """

        if not self.is_main:
            win32.Dispatch(self._prog_id_infoplayer5).RestartPlayback() # type: ignore
        else:
            print('restarting infoplayer')

    def sleep(self, secs: float):
        """
        The sleep function is a convenience function that wraps the sleep method of the scala player.
        It is used to add pauses in an API call sequence while testing. The unit of time is milliseconds.

        :param self: Used to access the instance of this class.
        :param secs:float: Used to specify the number of seconds to sleep.
        :return: None if the player is not in main mode.

        :doc-author: Trelent
        """

        if not self.is_main:
            self._scalaplayer.Sleep(secs * 1000) # type: ignore
        else:
            print('Sleeping for {} seconds'.format(secs))

    def find_content(self, path: str):
        """
        The find_content function is used to find the path of a file in the content folder.
        It will first check if there is an exact match for the path, and then it will try to find a partial match by removing folders from
        the end of the path one at a time. It returns None if no matches are found.

        :param self: Used to access the current object.
        :param path:str: Used to find the content of a file.
        :return: the path of the content file.

        :doc-author: Trelent
        """

        _path = path.replace('//', '\\')
        content_path = self._lock_content(_path)

        if content_path:
            path = content_path.string
            del content_path
            return path
        elif not self.is_main:
            self.error(f'The path "{path}" does not exists')
            return None
        else:
            print('searched for absolute path')
            return None

    def install_content(self, abspath: str, subsubfolders: Optional[str] = None):
        """
        The install_content function installs a file in the script folder.

        :param self: Used to access the script object itself.
        :param abspath:str: Used to specify the path to the file that is.
        :param subsubfolders:Optional[str]=None: Used to install the content in a subfolder of the script folder.
        :return: nothing.

        :doc-author: Trelent
        """

        if not os.path.isfile(abspath):
            self.error(f'File "{abspath}" does not exists or is not a file')

        if not subsubfolders is None:
            subfolder = os.path.join(self._script, subsubfolders)
        else:
            subfolder = self._script

        if not self.is_main:
            try:
                netic: Any = win32.Dispatch(self._prog_id_netic) # type: ignore
                netic.IntegrateContentLocally(abspath, subfolder)
            except com_error as error: # type: ignore
                self.warn('Could not install locally {}'.format(str(error))) # type: ignore

        else:
            print(f'integrating content from path {abspath} in subfolder {subfolder}')

        return 'Content:\\{}\\{}'.format(subfolder, os.path.basename(abspath))

    def download_media_temp(self, media_link: str, filename: Optional[str] = None, subsubfolders: Optional[str] = None):
        """
        The download_media_temp function downloads a media file from the given link and saves it to the specified folder.
        It is intended for downloading images, but can be used for other files as well.
        The function will try to download the file 10 times before giving up if there are connection errors.

        :param self: Used to refer to the instance of the class.
        :param media_link:str: Used to specify the link to the media.
        :param filename:Optional[str]=None: Used to specify a filename for the downloaded file.
        :param subsubfolders:Optional[str]=None: Used to create subfolders in the temp folder.
        :return: the path to the downloaded media.

        :doc-author: Trelent
        """

        if filename is None:
            media_filename = media_link.split('/').pop()
        else:
            media_filename = filename

        if subsubfolders is None:
            media_path = os.path.join(self.temp_folder, media_filename)
        else:
            media_path = os.path.join(
                self.temp_folder, subsubfolders, media_filename)

        response = requests.get(media_link, stream=True)

        if not response.ok:

            for _ in range(10):
                response = requests.get(media_link, stream=True)

                if response.ok:
                    break
                else:
                    if response.status_code == 500 or response.status_code == 503:
                        time.sleep(2)
                        continue
                    else:
                        break
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.error('Downloading image {} did not work because requests raised response error {}'.format(
                media_link, str(e)))

        with open(media_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)

        return media_path

    def download_root_temp(self, root: Element, filename: str) -> str:
        """
        The download_root_temp function downloads the root XMLElement
        and saves it to a temporary folder. It then returns the path of that file.

        :param self: Used to refer to the object itself.
        :param root:Element: Used to find the element with the correct name.
        :param filename:str: Used to create a path to the file in the temp folder.
        :return: a string.

        :doc-author: Trelent
        """

        path = os.path.join(self.temp_folder, filename)
        ElementTree(root).write(path)
        return path

    def _change_language(self) -> None:
        """
        The _change_language function changes the language of the application.
        It changes the language by setting a locale for date and time formatting.
        If this locale does not exist, it defaults to English (America).

        :param self: Used to access the instance variables of the class.
        :return: None.

        :doc-author: Trelent
        """

        if self.language == self.LANGUAGES['EN']:
            language_str = 'en_US'
            try:
                locale.setlocale(locale.LC_TIME, language_str)
            except locale.Error:
                language_str = 'English_America'
                locale.setlocale(locale.LC_TIME, language_str)
        else:
            language_str = 'nl_NL'
            try:
                locale.setlocale(locale.LC_TIME, language_str)
            except locale.Error:
                language_str = 'Dutch_Netherlands'
                locale.setlocale(locale.LC_TIME, language_str)

    def _create_find_me(self):
        """
        The _create_find_me function creates a file called find_me.txt in the find_me_path directory.

        :param self: Used to refer to the object that is calling the function.
        :return: a string that contains the name of the.

        :doc-author: Trelent
        """

        with open(self._find_me_path, 'w', encoding='utf-8') as file:
            file.write('find me!')

    def _get_debug(self) -> bool:
        """
        The _get_debug function returns the value of the debug field.

        :param self: Used to access the instance variables of the class.
        :return: the value of the _debug_field field.

        :doc-author: Trelent
        """

        debug_value = self._get_value(self._debug_field)
        return True if debug_value is None else debug_value

    def _get_language(self) -> int:
        """
        The _get_language function returns the language of the current page.

        :returns: The language of the current page as an integer value.

        :param self: Used to refer to the instance of the class.
        :return: an integer.

        :doc-author: Trelent
        """

        language_value = self._get_value(self._language_field)
        return self.LANGUAGES['NL'] if language_value is None else self.LANGUAGES.get(language_value, self.LANGUAGES['NL'])

    def _get_fi_key(self) -> str:
        """
        The _get_fi_key function is used to get the API key.
        The function takes no arguments and returns a string containing the API key.

        :param self: Used to refer to the object that is calling the function.
        :return: a string.

        :doc-author: Trelent
        """

        fi_api_key = self._get_value(self._fi_api_field)
        return '' if fi_api_key is None else fi_api_key

    def _get_player_uuid(self) -> str:
        """
        The _get_player_uuid function returns the player's UUID.

        :param self: Used to refer to the current instance of the class.
        :return: a string.

        :doc-author: Trelent
        """

        uuid = self._get_value(self._player_uuid_field)
        return '' if uuid is None else uuid

    def _get_keys(self) -> KeysView[str]:
        """
        The _get_keys function returns a list of all the keys in the scala player.

        :param self: Used to refer to the object that called the function.
        :return: a view of the keys in the script.

        :doc-author: Trelent
        """

        if not self.is_main:
            return self._scalaplayer.ListScalaScriptValues() # type: ignore
        else:
            print('Getting keys')
            temp: Dict[str, Any] = {}
            return temp.keys()

    def _get_value(self, key: str) -> Optional[Any]:
        """
        The _get_value function is a helper function that retrieves the value of a variable from the scala player.
        It is used by all other functions in this class to retrieve their values.

        :param self: Used to access the parent object.
        :param key:str: Used to get the value of a variable in the scala script.
        :return: the value of a variable.

        :doc-author: Trelent
        """

        if not self.is_main:
            if key in self._get_keys():
                value: Any = self._scalaplayer.GetScalaScriptValue(key) # type: ignore
                # if isinstance(value, (list, tuple)):
                #     value = self.Array(key, self)
                return value
            else:
                self.warn('variable {} from scala can not be found'.format(key))
                return None
        else:
            print('Getting value')
            return None

    def _set_value(self, key: str, value: Any):
        """
        The _set_value function is used to set scalascript values.
        It is only accessible from the main thread and it is not intended to be called directly.

        :param self: Used to access the class instance.
        :param key:str: Used to identify the value to be set.
        :param value:Any: Used to set the value of a scalascript variable.
        :return: None.

        :doc-author: Trelent
        """

        if not self.is_main:
            if key in self._get_keys():
                self._scalaplayer.SetScalaScriptValue(key, value) # type: ignore
            else:
                self.error(f'key {key} not found in scalascript values')
        else:
            print('Setting value')

    def _lock_content(self, path: str):
        """
        The _lock_content function locks the content of a file.

        :param self: Used to access the instance of the class.
        :param path:str: Used to determine if the file is locked.
        :return: a _StringAndLock object.

        :doc-author: Trelent
        """

        if not self.is_main:
            try:
                lockObj: Any = win32.Dispatch(self._prog_id_filelock) # type: ignore
                path = lockObj.LockScalaFile(path)
                item = self._StringAndLock(path)
                item.lockObj = lockObj
                return item
            except com_error as error: # type: ignore
                self.error('error while locking content {} because of com_error {}'.format(path, str(error))) # type: ignore

        else:
            print('Locking content')
            return None

    class _StringAndLock(str):
        """
        _StringAndLock A class method that acquires a string and acquires it .

        [extended_summary]

        Args:
            str ([type]): [description]
        """
        def __init__(self, string: str):
            """
            The __init__ function is the constructor for a class.
            It is called whenever an instance of the class is created.
            The __init__ function can take arguments, but self is always the first one.

            :param self: Used to distinguish between the instance of the class and other variables.
            :param string:str: Used to create the instance variable string.
            :return: self.

            :doc-author: Trelent
            """

            self.string = string
            self.lockObj: Any = None

        def __del__(self):
            self.lockObj.UnlockScalaFile()

    class Array(MutableSequence[Any]):
        """
        Array Constructs an Array class with the given values .

        [extended_summary]

        Args:
            MutableSequence ([type]): [description]
        """
        def __init__(self, key: str, scala_player: Player) -> None:
            """
            The __init__ function is the constructor for a Python class.
            It is called when an instance of a class is created.
            The __init__ function can take arguments, but self is always the first one.
            Self points to the object that was just created and allows us to access its data members and functions.

            :param self: Used to reference the instance of the class.
            :param key:str: Used to identify the player in the game.
            :param scala_player: Used to create a Player object.
            :return: None.

            :doc-author: Trelent
            """

            self._key = key
            self._player: Player = scala_player
            value = self._player._get_value(self._key)
            self._item: List[Any] = list(value) if not value is None else []

        def __repr__(self) -> str:
            """
            The __repr__ function is what is called by the repr() built-in function and
            is responsible for returning a string representation of an object. The goal of
            __repr__ is to be unambiguous. More precisely, __repr__ must return a string that
            if passed to eval() will result in an identical object (see PEP 3141). Thus, the
            returned string should include information necessary to recreate the object.

            :param self: Used to refer to the instance of the object.
            :return: a string representation of the object.

            :doc-author: Trelent
            """

            return str(self)

        def __str__(self):
            """
            The __str__ function is called when an instance of the class is printed.
            It returns a string representation of the object, which can be used for debugging.

            :param self: Used to reference the current instance of the class.
            :return: a string representation of the object.

            :doc-author: Trelent
            """

            return str(self._item)

        def __getitem__(self, index: int):
            """
            The __getitem__ function is a special method that allows the class to be used as an iterable.
            The __getitem__ function is called with index values (or slices) and returns the corresponding objects.

            :param self: Used to access the instance variables of the class.
            :param index:int: Used to specify the index of the item you want to retrieve.
            :return: the value at the given index.

            :doc-author: Trelent
            """

            return self._item[index]

        def __setitem__(self, index: int, value: Any):
            """
            The __setitem__ function is a special method that allows the class to be used like a list.
            For example, if we have an instance of the MyList class named my_list, then my_list[0] = 1
            will set item 0 in the list to 1.

            :param self: Used to reference the instance of the class.
            :param index: Used to access the item in the list.
            :param value: Used to set the value of the item at index.
            :return: None.

            :doc-author: Trelent
            """

            self._item[index] = value
            self._player._set_value(self._key, tuple(self._item))

        def __delitem__(self, _):
            """
            The __delitem__ function is used to delete an item from the list.

            :param self: Used to access the instance of the class.
            :param _: Used to pass the key of the item being deleted.
            :return: None.

            :doc-author: Trelent
            """

            self._player.warn('deleting ScalaScript array items is not allowed')

        def __len__(self):
            """
            The __len__ function returns the number of items in the list.

            :param self: Used to access the attributes of the class.
            :return: the number of items in the list.

            :doc-author: Trelent
            """

            return len(self._item)

        def insert(self, index: int, value: Any) -> None:
            """
            The insert function inserts a value into the list at the given index.

            :param self: Used to access the instance attributes of the class.
            :param index:int: Used to specify the index at which to insert the value.
            :param value:Any: Used to pass the value to be inserted.
            :return: None.

            :doc-author: Trelent
            """

            self._player.warn('inserting ScalaScript array items is not allowed')

        def clear(self) -> None:
            """
            The clear function clears the screen.

            :param self: Used to refer to the instance of the class.
            :return: None.

            :doc-author: Trelent
            """

            self._player.warn('deleting ScalaScript array items is not allowed')

        def extend(self, values: Any) -> None:
            """
            The extend function adds a list of values to the end of an existing list.
               The function does not return anything.

            :param self: Used to reference the object itself.
            :param values:Any: Used to extend the list with any number of values.
            :return: None.

            :doc-author: Trelent
            """

            self._player.warn('extending ScalaScript array items is not allowed')

        def pop(self, index: int = -1):
            """
            The pop function removes and returns the last item in the list.
            The optional argument index allows you to pop an item at a specific index.

            :param self: Used to access the instance of the class.
            :param index:int=-1: Used to specify the index of the item to be removed.
            :return: the value that was removed from the list.

            :doc-author: Trelent
            """

            self._player.warn('deleting ScalaScript array items is not allowed')

        def remove(self, value: Any):
            """
            The remove function removes a value from the set.
            It does not return anything.

            :param self: Used to access the instance variables of the class.
            :param value:Any: Used to remove the value from the list.
            :return: the value that was removed.

            :doc-author: Trelent
            """

            self._player.warn('deleting ScalaScript array items is not allowed')

    class Variables(MutableMapping[str, Any]):
        """
        Variables Class method for creating Variables .

        [extended_summary]

        Args:
            MutableMapping ([type]): [description]
        """
        def __init__(self, scala_player: Player) -> None:
            """
            The __init__ function is the constructor for a class.
            It is called whenever you create an instance of a class.
            The __init__ function can take arguments, but self is always the first one.
            Self is just a reference to the instance of the class.
            If you add other arguments to the __init__ function, they are interpreted as attributes that will be set on that object.

            :param self: Used to reference the instance of the object.
            :param scala_player:Player: Used to pass the player object from the Scala code to Python.
            :return: None.

            :doc-author: Trelent
            """


            self._player: Player = scala_player

        def __delitem__(self, _) -> None:
            """
            The __delitem__ function is used to delete an item from the list. It takes in a key as its input and deletes the
            item at that index.

            :param self: Used to refer to the instance of the class.
            :param _: Used to indicate that the parameter is private.
            :return: None.

            :doc-author: Trelent
            """

            self._player.warn('variable from scala can not be deleted')

        def __iter__(self) -> Iterator[str]:
            """
            The __iter__ function returns an iterator that can iterate over the keys of a dictionary.

            This is useful for when you want to write your own for loop to iterate over the keys of a dictionary.

            :param self: Used to access the instance variables of the class.
            :return: an iterator object.

            :doc-author: Trelent
            """

            for key in self._player._get_keys():
                yield key

        def __len__(self) -> int:
            """
            The __len__ function returns the number of items in the collection.

            Parameters:
                None
            Returns:
                The number of items in the collection as an integer.

            :param self: Used to access the instance's attributes.
            :return: the length of the list.

            :doc-author: Trelent
            """

            return len(self._player._get_keys())

        def __getitem__(self, key: str) -> Any:
            """
            The __getitem__ function is a special method that allows the class to be used as an array.
            For example, if you have a class called MyClass and it has an __init__ function that takes self and name as arguments,
            you can create a new instance of MyClass by writing: my_object = MyClass('value')
            You would then be able to access the value by calling: my_object['name']

            :param self: Used to access the instance variables.
            :param key:str: Used to access the dictionary.
            :return: the value of the key.

            :doc-author: Trelent
            """

            return self._player._get_value(key)

        def __setitem__(self, key: str, value: Any):
            """
            The __setitem__ function is used to set a value in the dictionary.
            If the key is not found, it will create a new entry with that key and assign it to that value.
            If the key is found, then it will update its corresponding value.

            :param self: Used to access the instance of the class that called it.
            :param key:str: Used to specify the name of the variable to be set.
            :param value:Any: Used to set the value of the key:str parameter.
            :return: :.

            :doc-author: Trelent
            """

            if isinstance(value, (tuple, list)):
                _array = self._player.Array(key, self._player)
                for i, element in enumerate(value): # type: ignore
                    _array[i] = element
            else:
                self._player._set_value(key, value)

        def __contains__(self, key: str):
            """
            The __contains__ function is used to check if a key is in the dictionary.
            It returns True or False depending on whether the key is found.

            :param self: Used to refer to the object that contains the function.
            :param key:str: Used to determine if the key is in the dictionary.
            :return: a boolean value.

            :doc-author: Trelent
            """

            return (key in self._player._get_keys())

        def keys(self) -> KeysView[str]:
            """
            The keys function returns a view of the keys in the dictionary.
            The returned object is itself a set-like object that provides a view
            of the keys currently defined in this dictionary. For example:
            >>> d = {'a': 1, 'b': 2}
            >>> list(d.keys())
            ['a', 'b']

            :param self: Used to refer to the object itself.
            :return: a view of the dictionary’s keys.

            :doc-author: Trelent
            """

            return self._player._get_keys()

        def items(self) -> Generator[Tuple[str, Any], None, None]:
            """
            The items function returns a view of the dictionary's items, as key-value pairs.
            The items are not in any particular order.

            :param self: Used to refer to the instance of the class.
            :return: a view of the player's inventory.

            :doc-author: Trelent
            """

            for key in self._player._get_keys():
                yield key, self._player._get_value(key)

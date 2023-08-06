from __future__ import annotations

import json
import logging
import os
import shutil
from datetime import datetime
from typing import Any, Dict, List, MutableSequence, Optional, Union, overload

import ipinfo
import requests
from requests.models import Response
from scala_wrapper.utils import typedef


def get_id(value: Optional[Dict[str, Any]]) -> Optional[int]:
    if not value is None:
        return value.get('id')
    return None

def get_name(value: Optional[Dict[str, Any]]) -> Optional[str]:
    if not value is None:
        return value.get('name')
    return None

@overload
def get_list(value: Optional[List[Union[Dict[str, Any], int]]], data: ContentManager.CategoryList) -> List[ContentManager.Category]:
    ...

@overload
def get_list(value: Optional[List[Union[Dict[str, Any], int]]], data: ContentManager.DistributionServerList) -> List[ContentManager.DistributionServer]:
    ...

@overload
def get_list(value: Optional[List[Union[Dict[str, Any], int]]], data: ContentManager.ExModuleList) -> List[ContentManager.ExModule]:
    ...

@overload
def get_list(value: Optional[List[Union[Dict[str, Any], int]]], data: ContentManager.MediaList) -> List[ContentManager.Media]:
    ...

@overload
def get_list(value: Optional[List[Union[Dict[str, Any], int]]], data: ContentManager.ResourceList) -> List[ContentManager.Resource]:
    ...

@overload
def get_list(value: Optional[List[Union[Dict[str, Any], int]]], data: ContentManager.PlayerGroupList) -> List[ContentManager.PlayerGroup]:
    ...

@overload
def get_list(value: Optional[List[Union[Dict[str, Any], int]]], data: ContentManager.PlayerList) -> List[ContentManager.Player]:
    ...

@overload
def get_list(value: Optional[List[Union[Dict[str, Any], int]]], data: ContentManager.RoleList) -> List[ContentManager.Role]:
    ...

@overload
def get_list(value: Optional[List[Union[Dict[str, Any], int]]], data: ContentManager.UserList) -> List[ContentManager.User]:
    ...

@overload
def get_list(value: Optional[List[Union[Dict[str, Any], int]]], data: ContentManager.WorkgroupList) -> List[ContentManager.Workgroup]:
    ...

def get_list(
    value: Optional[List[Union[Dict[str, Any], int]]],
    data: Union[
        ContentManager.CategoryList,
        ContentManager.DistributionServerList,
        ContentManager.ExModuleList,
        ContentManager.MediaList,
        ContentManager.PlayerGroupList,
        ContentManager.PlayerList,
        ContentManager.ResourceList,
        ContentManager.RoleList,
        ContentManager.UserList,
        ContentManager.WorkgroupList,
    ]
):
    temp: List[Any] = []
    if not value is None:
        for item in value:
            if isinstance(item, int):
                d = data.get(item)
                if d is None:
                    continue
                temp.append(d)
            else:
                item_id = get_id(item)
                if item_id is None:
                    item_id = get_name(item)
                    if item_id is None:
                        continue
                d = data.get(item_id)
                if d is None:
                    continue
                temp.append(d)
    return temp

def search_children(search: Union[int, str], children: List[Any], int_attr: str, str_attr: str, child_attr: str) -> Optional[Any]:
    for elem in children:
        if isinstance(search, int):
            if getattr(elem, int_attr) == search:
                return elem
        else:
            if getattr(elem, str_attr) == search:
                return elem

        temp = search_children(search, getattr(elem, child_attr), int_attr, str_attr, child_attr)
        if not temp is None:
            return temp

    return None

@overload
def clean_data(data: Dict[Any, Any]) -> Optional[Dict[Any, Any]]:
    ...

@overload
def clean_data(data: List[Any]) -> Optional[List[Any]]:
    ...

def clean_data(data: Union[Dict[Any, Any], List[Any]]):
    if isinstance(data, dict):
        for key, value in data.copy().items():
            if value is None:
                del data[key]

            if isinstance(value, list) or isinstance(value, dict):
                c_data = clean_data(value)

                if not c_data is None:
                    data[key] = c_data
                else:
                    del data[key]

        if len(data) > 0:
            return data
        else:
            return None
    else:
        for i, elem in enumerate(data):
            if elem is None:
                data.remove(elem)

            if isinstance(elem, list) or isinstance(elem, dict):
                c_data = clean_data(elem)

                if not c_data is None:
                    data[i] = c_data
                else:
                    data.pop(i)
        if len(data) > 0:
            return data
        else:
            return None

class ContentManager:
    def __init__(self, username: str, password: str, cm_url: str, client: Optional[str] = None, short: Optional[str] = None, client_id: Optional[int] = None, ip_handler: Optional[str] = None) -> None:
        self.client = client
        self.short = short
        self.client_id = client_id
        self.cm_url = cm_url
        self.username = username
        self.password = password
        self.air_id = None
        self.version = None
        self.ip_handler = ipinfo.getHandler(ip_handler) if not ip_handler is None else None
        self.last_load = datetime.now()

        self.approvalstatuses = self.ApprovalStatusList(self, [])
        self.categories = self.CategoryList(self, [])
        self.channels = self.ChannelList(self, [])
        self.distributionservers = self.DistributionServerList(self, [])
        self.ex_modules = self.ExModuleList(self, [])
        self.licenses = self.LicenseList(self, [])
        self.media = self.MediaList(self, [])
        self.networks = self.NetworkList(self, [])
        self.playergroups = self.PlayerGroupList(self, [])
        self.playerhealths = self.PlayerHealthList(self, [])
        self.player_metadatas = self.PlayerMetadataList(self, [])
        self.players = self.PlayerList(self, [])
        self.playlists = self.PlaylistList(self, [])
        self.resources = self.ResourceList(self, [])
        self.roles = self.RoleList(self, [])
        self.templates = self.TemplateList(self, [])
        self.users = self.UserList(self, [])
        self.workgroups = self.WorkgroupList(self, [])

        self.login()
        self.get_version()

    """ BASIC FUNCTIONALITY """
    def request(self, method: str, path: str, params: Optional[Dict[Any, Any]] = None, headers: Optional[Dict[Any, Any]] = None, data: str = '', debug_key: Optional[str] = None) -> Dict[Any, Any]:
        params = params if not params is None else {}
        headers = headers if not headers is None else {}
        headers.update(self.header)
        logging.info(f"{method} - {path}")

        if method.lower() == "delete":
            self.__delete(path, headers)
            return {"success": True}

        response_end = None
        offset = 0
        new = True

        while True:
            try:
                while new:
                    if method.lower() == "get":
                        params['offset'] = offset
                        params['limit'] = params.get("limit") if not params.get("limit") is None else 1000
                    response: Response =  requests.request(method, f'{self.cm_url}{path}', params=params, headers=headers, data=data)

                    if not response.ok:
                        logging.warning(f"Something went wrong when requesting {path} via {method}")
                        if response.status_code == 401:
                            logging.warning('login token expired requesting new one and trying again')
                            self.login()
                            headers.update(self.header)
                        logging.error(f"ERROR on {path} - code {response.status_code}")
                        logging.info(response.text)
                        continue

                    response_json: Union[List[Any], Dict[str, Any]] = response.json()

                    if isinstance(response_json, list):
                        response_json = {'list': response_json, 'count': 0}

                    if response_json.get('count', 0) < offset + params.get('limit', float('inf')):
                        new = False
                    else:
                        offset += params.get('limit', 0)

                    if response_end is None:
                        response_end = response_json
                    else:
                        response_end['list'].extend(response_json['list'])

                if response_end is None:
                    raise Exception('No response')

                debug_path = "cm_responses.json"
                debug_path_old = "cm_responses_old.json"
                if os.path.isfile(debug_path):
                    with open(debug_path, "r") as f:
                        try:
                            data_ = json.load(f)
                            shutil.copyfile(debug_path, debug_path_old)
                        except ValueError:
                            data_ = {}
                            pass
                else:
                    data_ = {}

                if not debug_key is None:
                    key = debug_key
                else:
                    key = f'{method} - {path}'

                if not key in data_.keys():
                    data_[key] = {}

                with open(debug_path, "w") as f:
                    if isinstance(response_end, list):
                        data_[key] = typedef.process_type(response_end, data_[key], False)
                        json.dump(data_, f)
                    else:
                        data_[key] = typedef.type_def_dict(response_end, data_[key], False)
                        json.dump(data_, f)

                return response_end

            except requests.exceptions.ConnectionError as e:
                logging.error(e)
                continue
            except requests.exceptions.ReadTimeout as e:
                logging.error(e)
                continue

    def __delete(self, path: str, headers: Optional[Dict[Any, Any]] = None):
        headers = headers if not headers is None else {}
        headers.update(self.header)
        while True:
            try:
                requests.delete(f'{self.cm_url}{path}', headers=headers)
                return
            except requests.exceptions.ConnectionError as e:
                logging.error(e)
                continue
            except requests.exceptions.ReadTimeout as e:
                logging.error(e)
                continue

    def login(self):
        payload: Dict[str, Union[str, bool]] = {
            'username': self.username,
            'password': self.password,
            'rememberMe': True
        }

        payload_str = json.dumps(payload)

        headers: Dict[str, str] = {
            'Content-type': 'application/json'
        }

        response = None

        while True:
            try:
                response = requests.post(f'{self.cm_url}/auth/login', data=payload_str, headers=headers)
            except requests.exceptions.ConnectionError as e:
                logging.error(e)
                continue
            break

        if response is None:
            raise Exception('Login Failed')
        else:
            response_json: Dict[str, Any] = response.json()

            self.api_token = response_json.get('apiToken')

            if self.api_token is None:
                raise Exception('No ApiToken found')
            else:
                self.header = {
                    'ApiToken': self.api_token,
                    'Content-Type': 'application/json'
                }

            self.user = self.users.append(ContentManager.User(self, response_json.get('user', {})))
            self.network = self.networks.get(get_id(response_json.get('network')))

            if self.network is None:
                raise Exception('No Network id found')

            self.token = response_json.get('token')
            self.api_license_token = response_json.get('apiLicenseToken')

            server_time = response_json.get('serverTime')

            if not server_time is None:
                self.time_dif_gmt = datetime.strptime(server_time.get('datetime', ''), '%Y-%m-%d %H:%M:%S') - datetime.strptime(server_time.get('gtmDatetime'), '%Y-%m-%d %H:%M:%S GMT')

    """ SETTERS OBJECT """
    def set_airtable_id(self, air_id: Optional[str]):
        self.air_id = air_id

    """ GETTERS ONLINE """

    def get_version(self):
        response = self.request('get', '/misc/productinfo')

        self.version: Optional[str] = response.get('version')

    """ APPROVALSTATUS """
    class ApprovalStatus:
        def __init__(self, cm: ContentManager, json: Dict[str, Any]) -> None:
            self.cm = cm
            self.unpack_json(json)

        def unpack_json(self, json: Dict[str, Any]):
            self.descritpion: Optional[str] = json.get('description')
            self.status: Optional[str] = json.get('status')
            self.prettifyStatus: Optional[str] = json.get('prettifyStatus')

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']

            for name, use in kwargs.items():
                #testing
                pass

            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

    class ApprovalStatusList(MutableSequence[ApprovalStatus]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.ApprovalStatus]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/approvalStatus')

            for elem in response.get('list', []):
                item = ContentManager.ApprovalStatus(self.cm, elem)
                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.ApprovalStatus]:
            if search is None:
                return None
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    logging.warning("Int is not possible to search")
                    return None
                else:
                    if elem.status == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    logging.warning("Int is not possible to search")
                    return None
                else:
                    if elem.status == search:
                        return elem

            logging.info(f'ApprovalStatus with {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.ApprovalStatus) -> None:
            self.__data.append(value)

    """ CATEGORY """
    class Category:
        def __init__(self, cm: ContentManager,  json: Dict[str, Any]) -> None:
            self.cm = cm
            self.unpack_json(json)

        def unpack_json(self, json: Dict[str, Any]):
            self.children: List[ContentManager.Category] = [ContentManager.Category(self.cm, elem) for elem in json.get('children', [])]
            self.description: Optional[str] = json.get('description')
            self.id: Optional[int] = json.get('id')
            self.name: Optional[str] = json.get('name')
            self.parentId: Optional[int] = json.get('parentId')

        def unpack_usage_json(self, json: Dict[str, Any]):
            self.messagesCount: Optional[int] = json.get('messagesCount')
            self.mediaCount: Optional[int] = json.get('mediaCount')
            self.templatesCount: Optional[int] = json.get("templatesCount")
            self.playlistsCount: Optional[int] = json.get('playlistsCount')
            self.remotePublishLocationsCount: Optional[int] = json.get('remotePublishLocationsCount')

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']

            for name, use in kwargs.items():
                if name == "link" and use:
                    data.pop('parentId', None)
                    data.pop('description', None)
                    data['children'] = [elem.json(link=True) for elem in self.children]


            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

        @staticmethod
        def create(cm: ContentManager, name: str, parentId: Optional[int] = None, children: Optional[Union[List[ContentManager.Category], List[int]]] = None, description: Optional[str] = None):
            children = children if not children is None else []
            parentId = parentId if not parentId is None else 0

            if len(children) > 0:
                if isinstance(children[0], int):
                    children_list = [cm.categories.get(elem) for elem in children if isinstance(elem, int)]
                    children_list = [elem for elem in children_list if not elem is None]
                else:
                    children_list = children
            else:
                children_list = children

            if not all(isinstance(elem, ContentManager.Category) for elem in children_list):
                raise Exception("Expected all children to be of type category")

            data = {
                "name": name,
                "parentId": parentId,
                "description": description,
                "children": [elem.json(link=True) for elem in children_list if isinstance(elem, ContentManager.Category)]
            }

            response = cm.request('post', '/categories', data=json.dumps(data))

            cm.categories.append(ContentManager.Category(cm, response))

        def delete(self):
            self.cm.__delete(f'/categories/{self.id}', {})

        def usage(self):
            response = self.cm.request('get', '/categories/usage', params={'ids': self.id})

            self.unpack_usage_json(response)

            return response

    class CategoryList(MutableSequence[Category]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.Category]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/categories')

            for elem in response.get('list', []):
                item = ContentManager.Category(self.cm, elem)
                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.Category]:
            if search is None:
                return None
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            logging.info(f'Category with {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.Category) -> None:
            self.__data.append(value)

    """ CHANNEL """
    class Channel:
        def __init__(self, cm: ContentManager, json: Dict[str, Any]) -> None:
            self.cm = cm
            self.unpack_json(json)

        def unpack_json(self, json: Dict[str, Any]):
            non_scheduled_playlist_id = get_id(json.get('nonScheduledPlaylist'))

            self.alternateSupport: Optional[bool] = json.get('alternateSupport')
            self.audioControlledByAdManager: Optional[bool] = json.get('audioControlledByAdManager')
            self.campaignChannel: Optional[bool] = json.get('campaignChannel')
            self.campaignClone: Optional[bool] = json.get('campaignClone')
            self.description: Optional[str] = json.get('description')
            self.frameset: ContentManager.Channel.FrameSet = ContentManager.Channel.FrameSet(self, json.get('frameset'))
            self.id: Optional[int] = json.get('id')
            self.lastModified: Optional[str] = json.get('lastModified')
            self.maxFrameAllowed: Optional[int] = json.get('maxFrameAllowed')
            self.maxPixelAllowed: Optional[int] = json.get('maxPixelAllowed')
            self.muteAudioFromVisual: Optional[bool] = json.get("muteAudioFromVisual")
            self.name: Optional[str] = json.get('name')
            self.nonScheduledPlaylist: Optional[ContentManager.Playlist] = self.cm.playlists.get(non_scheduled_playlist_id)
            self.playDedicatedAudioTrack: Optional[bool] = json.get('playDedicatedAudioTrack')
            self.playerCount: int = json.get('playerCount', 0)
            self.playerMetadataValues: List[ContentManager.Channel.MetadataValue] = [ContentManager.Channel.MetadataValue(self, elem) for elem in json.get('playerMetadataValues', [])]
            self.readOnly: Optional[bool] = json.get('readOnly')
            self.triggerSupport: Optional[bool] = json.get('triggerSupport')
            self.type: Optional[str] = json.get('type')
            self.variables: List[ContentManager.Channel.Variable] = [ContentManager.Channel.Variable(self, elem) for elem in json.get('variables', [])]
            self.workgroups: List[ContentManager.Workgroup] = get_list(json.get('workgroups'), self.cm.workgroups)

        def get_playlists(self) -> List[ContentManager.Playlist]:
            temp: List[ContentManager.Playlist] = []
            for frame in self.frameset.frames:
                for timeslot in frame.timeslots:
                    if not timeslot.playlist is None:
                        if not timeslot.playlist in temp:
                            temp.append(timeslot.playlist)

                if not frame.eventtriggers is None:
                    for eventtrigger in frame.eventtriggers:
                        if not eventtrigger.playlist is None:
                            if not eventtrigger.playlist in temp:
                                temp.append(eventtrigger.playlist)

            return temp

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']

            for name, use in kwargs.items():
                if name == 'player_update' and use:
                    data = {k:v for k,v in data.items() if k in ['campaignChannel', 'campaignClone', 'id', 'name']}

            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

        class FrameSet:
            def __init__(self, channel: ContentManager.Channel, json: Optional[Dict[str, Any]]) -> None:
                json = json if not json is None else {}
                self.channel = channel
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.campaignFrameset: Optional[bool] = json.get('campaignFrameset')
                self.eventTriggersCount: int = json.get('eventTriggersCount', 0)
                self.frames: List[ContentManager.Channel.FrameSet.Frame] = [ContentManager.Channel.FrameSet.Frame(self, elem) for elem in json.get('frames', [])]
                self.framesCounter: int = json.get('framesCounter', 0)
                self.height: Optional[int] = json.get('height')
                self.id: Optional[int] = json.get('id')
                self.name: Optional[str] = json.get('name')
                self.timeslotsCount: int = json.get('timeslotsCount', 0)
                self.width: Optional[int] = json.get('width')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['channel']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data


            class Frame:
                def __init__(self, frameset: ContentManager.Channel.FrameSet, json: Optional[Dict[str, Any]]) -> None:
                    json = json if not json is None else {}
                    self.frameset = frameset
                    self.unpack_json(json)

                def unpack_json(self, json: Dict[str, Any]):
                    alternate_playlist_id = get_id(json.get('alternatePlaylist'))

                    self.alternatePlaylist: Optional[ContentManager.Playlist] = self.frameset.channel.cm.playlists.get(alternate_playlist_id)
                    self.alternateType: Optional[str] = json.get('alternateType')
                    self.autoscale: Optional[str] = json.get('autoscale')
                    self.campaignTarget: Optional[bool] = json.get('campaignTarget')
                    self.color: Optional[str] = json.get('color')
                    self.controlledByAdManager: Optional[bool] = json.get('controlledByAdManager')
                    self.eventTriggersCount: int = json.get('eventTriggersCount', 0)
                    self.eventtriggers: List[ContentManager.Channel.FrameSet.Frame.EventTrigger] = []
                    self.height: Optional[int] = json.get('height')
                    self.hidden: Optional[bool] = json.get('hidden')
                    self.id: Optional[int] = json.get('id')
                    self.left: Optional[int] = json.get('left')
                    self.name: Optional[str] = json.get('name')
                    self.timeTriggersCount: int = json.get('timeTriggersCount', 0)
                    self.timeslots: List[ContentManager.Channel.FrameSet.Frame.Timeslot] = []
                    self.timeslotsCount: int = json.get('timeslotsCount', 0)
                    self.timetriggers: List[ContentManager.Channel.FrameSet.Frame.TimeTrigger] = []
                    self.top: Optional[int] = json.get('top')
                    self.width: Optional[int] = json.get('width')
                    self.zOrder: Optional[int] = json.get('zOrder')

                def json(self, **kwargs: bool):
                    data = vars(self)

                    data = data.copy()


                    del data['frameset']

                    for name, use in kwargs.items():
                        #testing
                        pass

                    for k, v in data.items():
                        try:
                            if isinstance(data[k], list):
                                for i, elem in enumerate(data[k]):
                                    try:
                                        data[k][i] = elem.json(**kwargs)
                                    except Exception:
                                        continue
                            else:
                                data[k] = v.json(**kwargs)
                        except Exception:
                            continue

                    data = clean_data(data)

                    if data is None:
                        return data

                    return data

                class Timeslot:
                    def __init__(self, frame: ContentManager.Channel.FrameSet.Frame, json: Dict[str, Any]) -> None:
                        self.frame = frame
                        self.unpack_json(json)

                    def unpack_json(self, json: Dict[str, Any]):
                        alternate_playlist_id = get_id(json.get('alternatePlaylist'))
                        playlist_id = get_id(json.get('playlist'))

                        self.alternatePlaylist: Optional[ContentManager.Playlist] = self.frame.frameset.channel.cm.playlists.get(alternate_playlist_id)
                        self.alternateType: Optional[str] = json.get('alternateType')
                        self.audioDucking: Optional[bool] = json.get('audioDucking')
                        self.color: Optional[str] = json.get('color')
                        self.controlledByAdManager: Optional[bool] = json.get('controlledByAdManager')
                        self.description: Optional[str] = json.get('description')
                        self.endDate: Optional[str] = json.get('endDate')
                        self.endTime: Optional[str] = json.get('endTime')
                        self.id: Optional[int] = json.get('id')
                        self.locked: Optional[bool] = json.get('locked')
                        self.monthPeriod: Optional[str] = json.get('monthPeriod')
                        self.name: Optional[str] = json.get('name')
                        self.playFullScreen: Optional[bool] = json.get('playFullScreen')
                        self.playlist: Optional[ContentManager.Playlist] = self.frame.frameset.channel.cm.playlists.get(playlist_id)
                        self.priorityClass: Optional[str] = json.get('priorityClass')
                        self.recurrencePattern: Optional[str] = json.get('recurrencePattern')
                        self.sortOrder: Optional[str] = json.get('sortOrder')
                        self.startDate: Optional[str] = json.get('startDate')
                        self.startTime: Optional[str] = json.get('startTime')
                        self.weekdays: Optional[List[str]] = json.get('weekdays')

                    def json(self, **kwargs: bool):
                        data = vars(self)

                        data = data.copy()


                        del data['frame']

                        for name, use in kwargs.items():
                            #testing
                            pass

                        for k, v in data.items():
                            try:
                                if isinstance(data[k], list):
                                    for i, elem in enumerate(data[k]):
                                        try:
                                            data[k][i] = elem.json(**kwargs)
                                        except Exception:
                                            continue
                                else:
                                    data[k] = v.json(**kwargs)
                            except Exception:
                                continue

                        data = clean_data(data)

                        if data is None:
                            return data

                        return data

                class EventTrigger:
                    def __init__(self, frame: ContentManager.Channel.FrameSet.Frame, json: Dict[str, Any]) -> None:
                        self.frame = frame
                        self.unpack_json(json)

                    def unpack_json(self, json: Dict[str, Any]):
                        playlist_id = get_id(json.get('playlist'))

                        self.audioDucking: Optional[bool] = json.get('audioDucking')
                        self.controlledByAdManager: Optional[bool] = json.get('controlledByAdManager')
                        self.id: Optional[int] = json.get('id')
                        self.itemsToPick: Optional[int] = json.get('itemsToPick')
                        self.playFullScreen: Optional[bool] = json.get('playFullScreen')
                        self.playlist: Optional[ContentManager.Playlist] = self.frame.frameset.channel.cm.playlists.get(playlist_id)
                        self.repeatTriggerResponse: Optional[str] = json.get('repeatTriggerResponse')
                        self.sortOrder: Optional[int] = json.get('sortOrder')

                        self.variable: ContentManager.Channel.FrameSet.Frame.EventTrigger.Variable = ContentManager.Channel.FrameSet.Frame.EventTrigger.Variable(self, json.get('variable'))

                    def json(self, **kwargs: bool):
                        data = vars(self)

                        data = data.copy()


                        del data['frame']

                        for name, use in kwargs.items():
                            #testing
                            pass

                        for k, v in data.items():
                            try:
                                if isinstance(data[k], list):
                                    for i, elem in enumerate(data[k]):
                                        try:
                                            data[k][i] = elem.json(**kwargs)
                                        except Exception:
                                            continue
                                else:
                                    data[k] = v.json(**kwargs)
                            except Exception:
                                continue

                        data = clean_data(data)

                        if data is None:
                            return data

                        return data

                    class Variable:
                        def __init__(self, eventtrigger: ContentManager.Channel.FrameSet.Frame.EventTrigger, json: Optional[Dict[str, Any]]) -> None:
                            json = json if not json is None else {}
                            self.eventtrigger = eventtrigger
                            self.unpack_json(json)

                        def unpack_json(self, json: Dict[str, Any]):
                            media_id = get_id(json.get('controlScript'))

                            self.controlScript: Optional[ContentManager.Media] = self.eventtrigger.frame.frameset.channel.cm.media.get(media_id)
                            self.id: Optional[int] = json.get('id')
                            self.name: Optional[str] = json.get('name')
                            self.sharedName: Optional[str] = json.get('sharedName')
                            self.type: Optional[str] = json.get('type')

                        def json(self, **kwargs: bool):
                            data = vars(self)

                            data = data.copy()


                            del data['eventtrigger']

                            for name, use in kwargs.items():
                                #testing
                                pass

                            for k, v in data.items():
                                try:
                                    if isinstance(data[k], list):
                                        for i, elem in enumerate(data[k]):
                                            try:
                                                data[k][i] = elem.json(**kwargs)
                                            except Exception:
                                                continue
                                    else:
                                        data[k] = v.json(**kwargs)
                                except Exception:
                                    continue

                            data = clean_data(data)

                            if data is None:
                                return data

                            return data

                class TimeTrigger:
                    def __init__(self, frame: ContentManager.Channel.FrameSet.Frame, json: Dict[str, Any]) -> None:
                        self.frame = frame
                        self.unpack_json(json)

                    def unpack_json(self, json: Dict[str, Any]):
                        playlist_id = get_id(json.get('playlist'))

                        self.audioDucking: Optional[bool] = json.get('audioDucking')
                        self.controlledByAdManager: Optional[bool] = json.get('controlledByAdManager')
                        self.days: Optional[List[str]] = json.get('days')
                        self.endDate: Optional[str] = json.get('endDate')
                        self.id: Optional[int] = json.get('id')
                        self.itemsToPick: Optional[int] = json.get('itemsToPick')
                        self.name: Optional[str] = json.get('name')
                        self.playFullScreen: Optional[bool] = json.get('playFullScreen')
                        self.playlist: Optional[ContentManager.Playlist] = self.frame.frameset.channel.cm.playlists.get(playlist_id)
                        self.recurrencePattern: Optional[str] = json.get('recurrencePattern')
                        self.repeatEndTime: Optional[str] = json.get('repeatEndTime')
                        self.repeatStartTime: Optional[str] = json.get('repeatStartTime')
                        self.repeatTriggerResponse: Optional[str] = json.get('repeatTriggerResponse')
                        self.sortOrder: Optional[int] = json.get('sortOrder')
                        self.startDate: Optional[str] = json.get('startDate')
                        self.time: Optional[str] = json.get('time')

                    def json(self, **kwargs: bool):
                        data = vars(self)

                        data = data.copy()


                        del data['frame']

                        for name, use in kwargs.items():
                            #testing
                            pass

                        for k, v in data.items():
                            try:
                                if isinstance(data[k], list):
                                    for i, elem in enumerate(data[k]):
                                        try:
                                            data[k][i] = elem.json(**kwargs)
                                        except Exception:
                                            continue
                                else:
                                    data[k] = v.json(**kwargs)
                            except Exception:
                                continue

                        data = clean_data(data)

                        if data is None:
                            return data

                        return data

        class Variable:
            def __init__(self, channel: ContentManager.Channel, json: Optional[Dict[str, Any]]) -> None:
                json = json if not json is None else {}
                self.channel = channel
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                media_id = get_id(json.get('controlScript'))

                self.controlScript: Optional[ContentManager.Media] = self.channel.cm.media.get(media_id)
                self.id: Optional[int] = json.get('id')
                self.name: Optional[str] = json.get('name')
                self.sharedName: Optional[str] = json.get('sharedName')
                self.type: Optional[str] = json.get('type')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['channel']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class MetadataValue:
            def __init__(self, channel: ContentManager.Channel, json: Optional[Dict[str, Any]]) -> None:
                self.channel = channel
                json = json if not json is None else {}
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                player_metadata_id = get_id(json.get('playerMetadata'))

                self.id: Optional[int] = json.get('id')
                self.playerMetadata: Optional[ContentManager.PlayerMetadata] = self.channel.cm.player_metadatas.get(player_metadata_id)
                self.value: Optional[str] = json.get('value')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['channel']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

    class ChannelList(MutableSequence[Channel]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.Channel]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/channels')

            for elem in response.get('list', []):
                item = ContentManager.Channel(self.cm, elem)

                for i, frame in enumerate(item.frameset.frames):
                    timeslots_response = self.cm.request('get', f'/channels/{item.id}/frames/{frame.id}/timeslots', debug_key="channel_timeslots")
                    eventtriggers_response = self.cm.request('get', f'/channels/{item.id}/frames/{frame.id}/eventtriggers', debug_key="channel_eventtriggers")
                    timetriggers_response = self.cm.request('get', f'/channels/{item.id}/frames/{frame.id}/timetriggers', debug_key="channel_timetriggers")

                    item.frameset.frames[i].timeslots = [ContentManager.Channel.FrameSet.Frame.Timeslot(frame, elem) for elem in timeslots_response.get('timeslots', [])]
                    item.frameset.frames[i].eventtriggers = [ContentManager.Channel.FrameSet.Frame.EventTrigger(frame, elem) for elem in eventtriggers_response.get('eventTriggers', [])]
                    item.frameset.frames[i].timetriggers = [ContentManager.Channel.FrameSet.Frame.TimeTrigger(frame, elem) for elem in timetriggers_response.get('timeTriggers', [])]

                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.Channel]:
            if search is None:
                return None
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            logging.info(f'Channel with {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.Channel) -> None:
            self.__data.append(value)

    """ DISTRIBUTIONSERVER """
    class DistributionServer:
        def __init__(self, cm: ContentManager,  json: Dict[str, Any]) -> None:
            self.cm = cm
            self.unpack_json(json)

        def unpack_json(self, json: Dict[str, Any]):
            self.auditSettings: ContentManager.DistributionServer.AuditSettings = ContentManager.DistributionServer.AuditSettings(self, json.get('auditSettings'))
            self.broadcastServer: ContentManager.DistributionServer.BroadcastServer = ContentManager.DistributionServer.BroadcastServer(self, json.get('broadcastServer'))
            self.description: Optional[str] = json.get('description')
            self.driver: Optional[str] = json.get('driver')
            self.driverOptions: List[ContentManager.DistributionServer.DriverOptions] = [ContentManager.DistributionServer.DriverOptions(self, elem) for elem in json.get('driverOptions', [])]
            self.iadeaServer: ContentManager.DistributionServer.IadeaServer = ContentManager.DistributionServer.IadeaServer(self, json.get('iadeaServer'))
            self.id: Optional[int] = json.get('id')
            self.monitoringSettings: ContentManager.DistributionServer.MonitoringSettings = ContentManager.DistributionServer.MonitoringSettings(self, json.get('monitoringSettings'))
            self.name: Optional[str] = json.get('name')
            self.omnicastServer: ContentManager.DistributionServer.OmnicastServer = ContentManager.DistributionServer.OmnicastServer(self, json.get('omnicastServer'))
            self.schedules: List[ContentManager.DistributionServer.Schedule] = [ContentManager.DistributionServer.Schedule(self, elem) for elem in json.get('schedules', [])]
            self.snapshotSettings: ContentManager.DistributionServer.SnapshotSettings = ContentManager.DistributionServer.SnapshotSettings(self, json.get('snapshotSettings'))
            self.synchronization: Optional[str] = json.get('synchronization')
            self.uuid: Optional[str] = json.get('uuid')
            # self.distributions Do not see added value to add this

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']

            for name, use in kwargs.items():
                if name == "player_update" and use:
                    data = {k:v for k,v in data.items() if k in ['driver', 'id', 'name', 'snapshotSettings']}

            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

        class AuditSettings:
            def __init__(self, server: ContentManager.DistributionServer, json: Optional[Dict[str, Any]]) -> None:
                json = json if not json is None else {}
                self.server = server
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.enabled: Optional[bool] = json.get('enabled')
                self.uploadFrequency: Optional[str] = json.get('uploadFrequency')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['server']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class BroadcastServer:
            def __init__(self, server: ContentManager.DistributionServer, json: Optional[Dict[str, Any]]) -> None:
                json = json if not json is None else {}
                self.server = server
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.delivery: Optional[str] = json.get('delivery')
                self.lastStatus: Optional[str] = json.get('lastStatus')
                self.logLevel: Optional[int] = json.get('logLevel')
                self.macAddress: Optional[str] = json.get('macAddress')
                self.password: Optional[str] = json.get('password')
                self.planRevision: Optional[int] = json.get('planRevision')
                self.playerCacheSize: Optional[int] = json.get('playerCacheSize')
                self.pollingInterval: Optional[int] = json.get('pollingInterval')
                self.serverUrl: Optional[str] = json.get('serverUrl')
                self.username: Optional[str] = json.get('username')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['server']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class DriverOptions:
            def __init__(self, server: ContentManager.DistributionServer, json: Optional[Dict[str, Any]]) -> None:
                json = json if not json is None else {}
                self.server = server
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.id: Optional[int] = json.get('id')
                self.key: Optional[str] = json.get('key')
                self.value: Optional[str] = json.get('value')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['server']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class IadeaServer:
            def __init__(self, server: ContentManager.DistributionServer, json: Optional[Dict[str, Any]]) -> None:
                json = json if not json is None else {}
                self.server = server
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.children: List[ContentManager.DistributionServer.IadeaServer] = [ContentManager.DistributionServer.IadeaServer(self.server, elem) for elem in json.get('children', [])]
                self.heartbeatErrorRetryRate: Optional[int] = json.get('heartbeatErrorRetryRate')
                self.logLevel: Optional[int] = json.get('logLevel')
                self.macAddress: Optional[str] = json.get('macAddress')
                self.parent: Optional[int] = get_id(json.get('parent'))
                self.planErrorRepollingRate: Optional[int] = json.get('planErrorRepollingRate')
                self.planPollingRate: Optional[int] = json.get('planPollingRate')
                self.planRevision: Optional[int] = json.get('planRevision')
                self.planStatusErrorRetryRate: Optional[int] = json.get('planStatusErrorRetryRate')
                self.playerHeartbeatRate: Optional[int] = json.get('playerHeartbeatRate')
                self.scheduleExpansionDays: Optional[int] = json.get('scheduleExpansionDays')
                self.scheduleRefreshTime: Optional[str] = json.get('scheduleRefreshTime')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['server']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class MonitoringSettings:
            def __init__(self, server: ContentManager.DistributionServer, json: Optional[Dict[str, Any]]) -> None:
                json = json if not json is None else {}
                self.server = server
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.diskSpaceReserve: Optional[int] = json.get('diskSpaceReserve')
                self.enabled: Optional[bool] = json.get('enabled')
                self.heartbeatRate: Optional[int] = json.get('heartbeatRate')
                self.overdueRate: Optional[int] = json.get('overdueRate')
                self.planStatusInterval: Optional[int] = json.get('planStatusInterval')
                self.purgeLogsAfter: Optional[int] = json.get('purgeLogsAfter')
                self.uploadLogs: Optional[bool] = json.get('uploadLogs')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['server']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class OmnicastServer:
            def __init__(self, server: ContentManager.DistributionServer, json: Optional[Dict[str, Any]]) -> None:
                json = json if not json is None else {}
                self.server = server
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.url: Optional[str] = json.get('url')
                self.username: Optional[str] = json.get('username')
                self.password: Optional[str] = json.get('password')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['server']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class Schedule:
            def __init__(self, server: ContentManager.DistributionServer, json: Optional[Dict[str, Any]]) -> None:
                json = json if not json is None else {}
                self.server = server
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                player_group_id = get_id(json.get('playerGroup'))

                self.dayOfWeek: Optional[str] = json.get('dayOfWeek')
                self.hours: Optional[str] = json.get('hours')
                self.id: Optional[int] = json.get('id')
                self.minutes: Optional[str] = json.get('minutes')
                self.playerGroup: Optional[ContentManager.PlayerGroup] = self.server.cm.playergroups.get(player_group_id)
                self.seconds: Optional[str] = json.get('seconds')
                self.type: Optional[str] = json.get('type')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['server']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class SnapshotSettings:
            def __init__(self, server: ContentManager.DistributionServer, json: Optional[Dict[str, Any]]) -> None:
                json = json if not json is None else {}
                self.server = server
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.connectionValid: Optional[bool] = json.get('connectionValid')
                self.enabled: Optional[bool] = json.get('enabled')
                self.interval: Optional[int] = json.get('interval')
                self.intervalNumSnapshots: Optional[int] = json.get('intervalNumSnapshots')
                self.intervalProfile: Optional[str] = json.get('intervalProfile')
                self.onDemandProfile: Optional[str] = json.get('onDemandProfile')
                self.onEventProfile: Optional[str] = json.get('onEventProfile')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['server']

                for name, use in kwargs.items():
                    if name == "player_update" and use:
                        data = {k:v for k,v in data.items() if k in ['connectionValid', 'enabled', 'interval', 'intervalNumSnapshots', 'intervalProfile', 'onDemandProfile', 'onEventProfile']}

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)

                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

    class DistributionServerList(MutableSequence[DistributionServer]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.DistributionServer]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/distributions')

            for elem in response.get('list', []):
                item = ContentManager.DistributionServer(self.cm, elem)
                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.DistributionServer]:
            if search is None:
                return None
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            logging.info(f'DistributionServer with {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.DistributionServer) -> None:
            self.__data.append(value)

    """ EXMODULE """
    class ExModule:
        def __init__(self, cm: ContentManager, json: Dict[str, Any]) -> None:
            self.cm = cm
            self.unpack_json(json)

        def unpack_json(self, json: Dict[str, Any]):
            self.description: Optional[str] = json.get('description')
            self.name: Optional[str] = json.get('name')
            self.total: Optional[int] = json.get('total')
            self.used: Optional[int] = json.get('used')
            self.value: Optional[str] = json.get('value')

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']

            for name, use in kwargs.items():
                #testing
                pass

            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

    class ExModuleList(MutableSequence[ExModule]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.ExModule]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/players/modules')

            for elem in response.get('list', []):
                item = ContentManager.ExModule(self.cm, elem)
                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.ExModule]:
            if search is None:
                return None
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    logging.warning('Int not possible for exModule')
                    return None
                else:
                    if elem.name == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    logging.warning('Int not possible for exModule')
                    return None
                else:
                    if elem.name == search:
                        return elem

            logging.info(f'ExModule with {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.ExModule) -> None:
            self.__data.append(value)

    """ LICENSE """
    class License:
        def __init__(self, cm: ContentManager, json: Dict[str, Any]) -> None:
            self.cm = cm
            self.unpack_json(json)

        def unpack_json(self, json: Dict[str, Any]):
            # self.featureLicenses TODO
            # self.playerLicenses TODO
            self.advantageCoverageUntil: Optional[str] = json.get('advantageCoverageUntil')
            self.basicDesignerSeats: Optional[int] = json.get('basicDesignerSeats')
            self.campaignSeats: Optional[int] = json.get('campaignSeats')
            self.campaignTargets: Optional[int] = json.get('campaignTargets')
            self.countSubNetworks: Optional[int] = json.get('countSubNetworks')
            self.dongleId: Optional[str] = json.get("dongleId")
            self.exModules: List[ContentManager.ExModule] = [elem for elem in [self.cm.ex_modules.get(get_name(elem)) for elem in json.get('exModules', [])] if not elem is None]
            self.hasAdManager: Optional[bool] = json.get('hasAdManager')
            self.isBetaDongle: Optional[bool] = json.get("isBetaDongle")
            self.isSoftDongle: Optional[bool] = json.get('isSoftDongle')
            self.isTrial: Optional[bool] = json.get('isTrial')
            self.isUsageUnlimited: Optional[bool] = json.get('isUsageUnlimited')
            self.name : Optional[str] = json.get('name')
            self.playerCals: Optional[int] = json.get('playerCals')
            self.playerCalsUnlimited: Optional[bool] = json.get('playerCalsUnlimited')
            self.playerClientAccessLicenses: Optional[str] = json.get('playerClientAccessLicenses')
            self.premiumDesignerSeats: Optional[int] = json.get('premiumDesignerSeats')
            self.productId: Optional[str] = json.get("productId")
            self.professionalDesignerSeats: Optional[int] = json.get('professionalDesignerSeats')
            self.scalaMaintenanceExpired: Optional[bool] = json.get('scalaMaintenanceExpired')
            self.scalaOutOfMaintenance: Optional[bool] = json.get('scalaOutOfMaintenance')
            self.softDongleLicenseTo: Optional[str] = json.get('softDongleLicenseTo')
            self.standardDesignerSeats: Optional[int] = json.get('standardDesignerSeats')
            self.trailDaysLeft: Optional[int] = json.get('trialDaysLeft')
            self.usageUntil: Optional[str] = json.get('usageUntil')
            self.usedCount: Optional[int] = json.get('usedCount')

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']

            for name, use in kwargs.items():
                #testing
                pass

            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

    class LicenseList(MutableSequence[License]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.License]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            if self.cm.network is None:
                raise Exception('Need current network')
            response: Dict[str, Any] = self.cm.request('get', f'/license/networks/{self.cm.network.id}')

            if response.get('list') is None:
                item = ContentManager.License(self.cm, response)
                self.__data.append(item)
            else:
                for elem in response.get('list', []):
                    item = ContentManager.License(self.cm, elem)
                    self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.License]:
            if search is None:
                return None
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    logging.warning("Int search not possible for license")
                    return None
                else:
                    if elem.name == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    logging.warning("Int search not possible for license")
                    return None
                else:
                    if elem.name == search:
                        return elem

            logging.info(f'License with {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.License) -> None:
            self.__data.append(value)

    """ MEDIA  """
    class Media:
        def __init__(self, cm: ContentManager, data: Dict[str, Any]) -> None:
            self.cm = cm
            self.unpack_json(data)

        def unpack_json(self, json: Dict[str, Any]):
            created_user_id = get_id(json.get('createdBy'))
            modified_user_id = get_id(json.get('modifiedBy'))
            template_id = get_id(json.get('template'))
            uploaded_user_id = get_id(json.get('uploadedBy'))

            self.approval: ContentManager.Media.Approval = ContentManager.Media.Approval(self, json.get('approval'))
            self.approvalDetail: ContentManager.Media.ApprovalDetail = ContentManager.Media.ApprovalDetail(self, json.get('approvalDetail'))
            self.approvalStatus: Optional[str] = json.get('approvalStatus')
            self.archived: Optional[bool] = json.get('archived')
            self.audioDucking: Optional[bool] = json.get('audioDucking')
            self.backgroundColor: Optional[str] = json.get('backgroundColor')
            self.broadcastPriority: Optional[str] = json.get('broadcastPriority')
            self.campaignMedia: Optional[bool] = json.get('campaignMedia')
            self.categories: List[ContentManager.Category] = get_list(json.get('categories'), self.cm.categories)
            self.createdBy: Optional[ContentManager.User] = self.cm.users.get(created_user_id)
            self.createdDate: Optional[str] = json.get('createdDate')
            self.description: Optional[str] = json.get('description')
            self.downloadPath: Optional[str] = json.get('downloadPath')
            self.duration: Optional[int] = json.get('duration')
            self.endValidDate: Optional[str] = json.get('endValidDate')
            self.fields: List[ContentManager.Media.Field] = [ContentManager.Media.Field(self, elem) for elem in json.get('fields', [])]
            self.generatingThumbnail: Optional[bool] = json.get('generatingThumbnail')
            self.hasSnapshot: Optional[bool] = json.get('hasSnapshot')
            self.hasUnapprovedElements: Optional[bool] = json.get('hasUnapprovedElements')
            self.height: Optional[int] = json.get('height')
            self.id: Optional[int] = json.get('id')
            self.input: Optional[str] = json.get('input')
            self.lastModified: Optional[str] = json.get('lastModified')
            self.length: Optional[int] = json.get('length')
            self.mediaItemFiles: List[ContentManager.Media.ItemFile] = [ContentManager.Media.ItemFile(self, elem) for elem in json.get('mediaItemFiles', [])]
            self.mediaType: Optional[str] = json.get('mediaType')
            self.messagesCount: int = json.get('messagesCount', 0)
            self.modifiedBy: Optional[ContentManager.User] = self.cm.users.get(modified_user_id)
            self.name: Optional[str] = json.get('name')
            self.neverArchive: Optional[bool] = json.get('neverArchive')
            self.originalCreatedDate: Optional[str] = json.get("originalCreatedDate")
            self.pages: Optional[int] = json.get('pages')
            self.path: Optional[str] = json.get('path')
            self.playFullscreen: Optional[bool] = json.get('playFullscreen')
            self.playlistsCount: int = json.get('playlistsCount', 0)
            self.prettifyDuration: Optional[str] = json.get('prettifyDuration')
            self.prettifyLength: Optional[str] = json.get('prettifyLength')
            self.prettifyType: Optional[str] = json.get('prettifyType')
            self.readOnly: Optional[bool] = json.get('readOnly')
            self.revision: Optional[int] = json.get('revision')
            self.saveAndApprove: Optional[bool] = json.get('saveAndApprove')
            self.snapshotInQueue: Optional[bool] = json.get('snapshotInQueue')
            self.startValidDate: Optional[str] = json.get('startValidDate')
            self.status: Optional[str] = json.get('status')
            self.template: Optional[ContentManager.Template] = self.cm.templates.get(template_id)
            self.templatesCount: int = json.get('templatesCount', 0)
            self.thumbnailDownloadPaths: ContentManager.Media.ThumbnailDownloadPaths = ContentManager.Media.ThumbnailDownloadPaths(self, json.get('thumbnailDownloadPaths'))
            self.uploadType: Optional[str] = json.get('uploadType')
            self.uploadedBy: Optional[ContentManager.User] = self.cm.users.get(uploaded_user_id)
            self.uri: Optional[str] = json.get('uri')
            self.validDateStatus: Optional[str] = json.get('validDateStatus')
            self.volume: Optional[int] = json.get('volume')
            self.webDavPath: Optional[str] = json.get('webDavPath')
            self.width: Optional[int] = json.get('width')
            self.workgroups: List[ContentManager.Workgroup] = get_list(json.get('workgroups'), self.cm.workgroups)

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']

            for name, use in kwargs.items():
                #testing
                pass

            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

        class ThumbnailDownloadPaths:
            def __init__(self, media: ContentManager.Media,  json: Optional[Dict[str, Any]]) -> None:
                self.media = media
                json = json if not json is None else {}
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.extraSmall: Optional[str] = json.get('extraSmall')
                self.small: Optional[str] = json.get('small')
                self.mediumSmall: Optional[str] = json.get('mediumSmall')
                self.medium: Optional[str] = json.get('medium')
                self.large: Optional[str] = json.get('large')

                ### UNUSED BY FIRST
                self.custom: Optional[str] = json.get('custom')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['media']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class ApprovalDetail:
            def __init__(self, media: ContentManager.Media,  json: Optional[Dict[str, Any]]) -> None:
                self.media = media
                json = json if not json is None else {}
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.id: Optional[int] = json.get('id')
                self.approvalStatus: Optional[str] = json.get('approvalStatus')

                user_id = get_id(json.get('user'))
                self.user: Optional[ContentManager.User] = self.media.cm.users.get(user_id)

                to_approve_id = get_id(json.get('toApprove'))
                self.toApprove: Optional[ContentManager.User] = self.media.cm.users.get(to_approve_id)

                by_approve_id = get_id(json.get('approvedBy'))
                self.approvedBy: Optional[ContentManager.User] = self.media.cm.users.get(by_approve_id)

                self.messageText: Optional[str] = json.get('messageText')
                self.lastModified: Optional[str] = json.get('lastModified')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['media']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class ItemFile:
            def __init__(self, media: ContentManager.Media,  json: Dict[str, Any]) -> None:
                self.media = media
                json = json if not json is None else {}
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.id: Optional[int] = json.get('id')
                self.filename: Optional[str] = json.get('filename')
                self.size: Optional[int] = json.get('size')
                self.prettifySize: Optional[str] = json.get('prettifySize')
                self.uploadDate: Optional[str] = json.get('uploadDate')
                self.version: Optional[int] = json.get('version')
                self.downloadPath: Optional[str] = json.get('downloadPath')
                self.originalFilename: Optional[str] = json.get('originalFilename')
                self.status: Optional[str] = json.get('status')
                self.uploadedBy: Optional[str] = json.get('uploadedBy')
                self.md5: Optional[str] = json.get('md5')

                self.thumbnailDownloadPaths: Optional[ContentManager.Media.ItemFile.ThumbnailDownloadPaths] = ContentManager.Media.ItemFile.ThumbnailDownloadPaths(self, json.get('thumbnailDownloadPaths'))

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['media']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

            class ThumbnailDownloadPaths:
                def __init__(self, itemfile: ContentManager.Media.ItemFile,  json: Optional[Dict[str, Any]]) -> None:
                    self.itemfile = itemfile
                    json = json if not json is None else {}
                    self.unpack_json(json)

                def unpack_json(self, json: Dict[str, Any]):
                    self.extraSmall: Optional[str] = json.get('extraSmall')
                    self.small: Optional[str] = json.get('small')
                    self.mediumSmall: Optional[str] = json.get('mediumSmall')
                    self.medium: Optional[str] = json.get('medium')
                    self.large: Optional[str] = json.get('large')

                    ### UNUSED BY FIRST
                    self.custom: Optional[str] = json.get('custom')

                def json(self, **kwargs: bool):
                    data = vars(self)

                    data = data.copy()


                    del data['itemfile']

                    for name, use in kwargs.items():
                        #testing
                        pass

                    for k, v in data.items():
                        try:
                            if isinstance(data[k], list):
                                for i, elem in enumerate(data[k]):
                                    try:
                                        data[k][i] = elem.json(**kwargs)
                                    except Exception:
                                        continue
                            else:
                                data[k] = v.json(**kwargs)
                        except Exception:
                            continue

                    data = clean_data(data)

                    if data is None:
                        return data

                    return data

        class Approval:
            def __init__(self, media: ContentManager.Media,  json: Optional[Dict[str, Any]]) -> None:
                self.media = media
                json = json if not json is None else {}
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.action: Optional[str] = json.get('action')
                self.userId: Optional[int] = json.get('integer')
                self.messageText: Optional[str] = json.get('messageText')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['media']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class Field:
            def __init__(self, media: ContentManager.Media,  json: Optional[Dict[str, Any]]) -> None:
                self.media = media
                json = json if not json is None else {}
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.id: Optional[int] = json.get('id')
                self.name: Optional[str] = json.get('name')
                self.displayName: Optional[str] = json.get('displayName')
                self.value: Optional[str] = json.get('value')
                self.templateId: Optional[int] = json.get('templateId')
                self.required: Optional[bool] = json.get('required')
                self.type: Optional[str] = json.get('type')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['media']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

    class MediaList(MutableSequence[Media]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.Media]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/media')

            for elem in response.get('list', []):
                item = ContentManager.Media(self.cm, elem)
                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.Media]:
            if search is None:
                return None

            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            logging.info(f'Media with {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.Media) -> None:
            self.__data.append(value)

    """ NETWORK """
    class Network:
        def __init__(self, cm: ContentManager, json: Dict[str, Any]) -> None:
            self.cm = cm
            self.unpack_json(json)

        def unpack_json(self, json: Dict[str, Any]):
            self.active: Optional[bool] = json.get('active')
            self.approvalMedia: Optional[bool] = json.get('approvalMedia')
            self.approvalMessage: Optional[bool] = json.get('approvalMessage')
            self.autoThumbnailGeneration: Optional[bool] = json.get('autoThumbnailGeneration')
            self.automaticPlaylistDurationCalculation: Optional[bool] = json.get('automaticPlaylistDurationCalculation')
            self.firstDay: Optional[str] = json.get('firstDay')
            self.id: Optional[int] = json.get('id')
            self.licenseState: Optional[str] = json.get('licenseState')
            self.maxDatabaseAge: Optional[int] = json.get('maxDatabaseAge')
            self.maxDownloadThreads: Optional[int] = json.get('maxDownloadThreads')
            self.name: Optional[str] = json.get('name')
            self.newsFeed: Optional[bool] = json.get('newsFeed')
            self.newsFeedUrl: Optional[str] = json.get('newsFeedUrl')
            self.passwordCheckCharTypes: Optional[bool] = json.get('passwordCheckCharTypes')
            self.passwordMinimumLength: Optional[int] = json.get('passwordMinimumLength')
            self.passwordUseLowercase: Optional[bool] = json.get('passwordUseLowercase')
            self.passwordUseNonAlphanumeric: Optional[bool] = json.get('passwordUseNonAlphanumeric')
            self.passwordUseNumbers: Optional[bool] = json.get('passwordUseNumbers')
            self.passwordUseUppercase: Optional[bool] = json.get('passwordUseUppercase')
            self.playbackAuditParser: Optional[bool] = json.get('playbackAuditParser')
            self.purgeDaysPlanGenHistory: Optional[int] = json.get('purgeDaysPlanGenHistory')
            self.senderEmailAddress: Optional[str] = json.get('snederEmailAddress')
            self.sessionTimeout: Optional[int] = json.get('sessionTimeout')
            self.showMessageFieldsInMultiplePages: Optional[bool] = json.get('showMessageFieldsInMultiplePages')
            self.smtpAuthentication: Optional[bool] = json.get('smtpAuthentication')
            self.smtpEnabled: Optional[bool] = json.get('smtpEnabled')
            self.smtpPort: Optional[int] = json.get('smtpPort')
            self.smtpServerAddress: Optional[str] = json.get('smtpServerAddress')
            self.smtpSsl: Optional[bool] = json.get('smtpSsl')
            self.smtpUsername: Optional[str] = json.get('smtpUsername')
            self.userPasswordExpiresIn: Optional[int] = json.get('userPasswordExpiresIn')
            self.userPasswordExpiresInMinutes: Optional[bool] = json.get('userPasswordExpiresInMinutes')
            self.viewReport: Optional[bool] = json.get('viewReport')

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']

            for name, use in kwargs.items():
                #testing
                pass

            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

    class NetworkList(MutableSequence[Network]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.Network]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/networks')

            for elem in response.get('list', []):
                item = ContentManager.Network(self.cm, elem)
                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.Network]:
            if search is None:
                return None
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            logging.info(f'Network with {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.Network) -> None:
            self.__data.append(value)

    """ PLAYER """
    class PlayerGroup:
        def __init__(self, cm: ContentManager, json: Dict[str, Any]) -> None:
            self.cm = cm
            self.unpack_json(json)

        def unpack_json(self, json: Dict[str, Any]):
            self.descritpion: Optional[str] = json.get('description')
            self.id: Optional[int] = json.get('id')
            self.name: Optional[str] = json.get('name')
            self.numberOfPlayers: Optional[int] = json.get('numberOfPlayers')

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']

            for name, use in kwargs.items():
                if name == 'player_update' and use:
                    data = {k:v for k,v in data.items() if k in ['id']}


            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

    class PlayerGroupList(MutableSequence[PlayerGroup]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.PlayerGroup]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/playergroup')

            for elem in response.get('list', []):
                item = ContentManager.PlayerGroup(self.cm, elem)
                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.PlayerGroup]:
            if search is None:
                return None
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            logging.info(f'Player with {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.PlayerGroup) -> None:
            old_ids = [elem.id for elem in self.__data]
            if not value.id in old_ids:
                self.__data.append(value)

    class PlayerHealth:
        def __init__(self, cm: ContentManager, json: Dict[str, Any]) -> None:
            self.cm = cm
            self.unpack_json(json)

        def unpack_json(self, json: Dict[str, Any]):
            self.alerted: Optional[bool] = json.get("alerted")
            self.cleared: Optional[bool] = json.get("cleared")
            self.clearedDate: Optional[str] = json.get("clearedDate")
            self.descriptionDebug: Optional[List[str]] = json.get("descriptionDebug")
            self.descriptionDetails: Optional[List[str]] = json.get("descriptionDetails")
            self.descriptionTech: Optional[List[str]] = json.get('descriptionTech')
            self.descriptionUser: Optional[List[str]] = json.get("descriptionUser")
            self.errorNumber: Optional[str] = json.get("errorNumber")
            self.first: Optional[str] = json.get("first")
            self.id: Optional[int] = json.get("id")
            self.last: Optional[str] = json.get("last")
            self.message: Optional[str] = json.get("message")
            self.playerCount: int = json.get("playerCount", 0)
            self.problemMessage: Optional[str] = json.get("problemMessage")
            self.problemNumber: Optional[int] = json.get("problemNumber")
            self.reported: int = json.get("reported", 0)
            self.reportedPlayers: List[ContentManager.PlayerHealth.ReportedPlayer] = [ContentManager.PlayerHealth.ReportedPlayer(self.cm, elem) for elem in json.get("reportedPlayers", [])]

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']

            for name, use in kwargs.items():
                #testing
                pass

            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

        class ReportedPlayer:
            def __init__(self, cm: ContentManager, json: Dict[str, Any]) -> None:
                self.cm = cm
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.id: Optional[int] = json.get("id")
                self.first: Optional[str] = json.get("first")
                self.last: Optional[str] = json.get("last")
                self.playerLogFile: Optional[str] = json.get("playerLogFile")
                self.reported: int = json.get("reported", 0)

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['cm']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

    class PlayerHealthList(MutableSequence[PlayerHealth]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.PlayerHealth]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/playerhealth')

            for elem in response.get('list', []):
                item = ContentManager.PlayerHealth(self.cm, elem)
                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.PlayerHealth]:
            if search is None:
                return None
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.problemMessage == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.problemMessage == search:
                        return elem

            logging.info(f'PlayerHealth with {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.PlayerHealth) -> None:
            self.__data.append(value)

    class PlayerMetadata:
        def __init__(self, cm: ContentManager, json: Dict[str, Any]) -> None:
            self.cm = cm
            self.unpack_json(json)

        def unpack_json(self, json: Dict[str, Any]):
            self.datatype: Optional[str] = json.get('datatype')
            self.id: Optional[int] = json.get('id')
            self.name: Optional[str] = json.get('name')
            self.order: Optional[int] = json.get('order')
            self.predefinedValues: List[ContentManager.PlayerMetadata.PredefinedValue] = [ContentManager.PlayerMetadata.PredefinedValue(self, elem) for elem in json.get('predefinedValues', [])]
            self.valueType: Optional[str] = json.get('valueType')

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']

            for name, use in kwargs.items():
                #testing
                pass

            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

        @staticmethod
        def create(cm: ContentManager, name: str, datatype: str, valuetype: str):
            name = name.replace('Player.', '')
            data = {
                'name': name,
                'datatype': datatype,
                'valueType': valuetype
            }

            cm.request('post', '/playerMetadata', data=json.dumps(data))

        class PredefinedValue:
            def __init__(self, metadata: ContentManager.PlayerMetadata, json: Optional[Dict[str, Any]]) -> None:
                json = json if not json is None else {}
                self.metadata = metadata
                self.unpack_json(json)

            def unpack_json(self, json:Dict[str,Any]) -> None:
                self.id: Optional[int] = json.get('id')
                self.sortOrder: Optional[int] = json.get('sortOrder')
                self.value: Optional[str] = json.get('value')
                self.variableId: Optional[int] = json.get('variableId')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['metadata']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

    class PlayerMetadataList(MutableSequence[PlayerMetadata]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.PlayerMetadata]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/playerMetadata')

            for elem in response.get('list', []):
                item = ContentManager.PlayerMetadata(self.cm, elem)
                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.PlayerMetadata]:
            if search is None:
                return None
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            logging.info(f'PlayerMetadata with {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.PlayerMetadata) -> None:
            self.__data.append(value)

    class Player:
        def __init__(self, cm: ContentManager,  json: Dict[str, Any]) -> None:
            self.cm = cm
            self.unpack_json(json)

        def unpack_json(self, json: Dict[str, Any]):
            distribution_server_id = get_id(json.get('distributionServer'))
            owner_workgroup_id = get_id(json.get('ownerWorkgroup'))
            # site_id = get_id(json.get('site'))

            self.active: Optional[str] = json.get('active')
            self.bandwidthThrottlingWindows: List[ContentManager.Player.BandwidthThrottlingWindow] = [ContentManager.Player.BandwidthThrottlingWindow(self, elem) for elem in json.get('bandwidthThrottlingWindows', [])]
            self.customId: Optional[str] = json.get('customId')
            self.description: Optional[str] = json.get('description')
            self.distributionServer: Optional[ContentManager.DistributionServer] = self.cm.distributionservers.get(distribution_server_id)
            self.downloadThreads: Optional[int] = json.get('downloadThreads')
            self.enabled: Optional[bool] = json.get('enabled')
            self.exModules: List[ContentManager.ExModule] = get_list(json.get('exModules'), self.cm.ex_modules)
            self.featureLicenseType: ContentManager.Player.FeatureLicense = ContentManager.Player.FeatureLicense(self, json.get('featureLicenseType'))
            self.id: Optional[int] = json.get('id')
            self.intervalSnapshotEnabled: Optional[bool] = json.get('intervalSnapshotEnabled')
            self.lastModified: Optional[str] = json.get('lastModified')
            self.limitDefaultBandwidth: Optional[int] = json.get('limitDefaultBandwidth')
            self.logLevel: Optional[str] = json.get('logLevel')
            self.mac: Optional[str] = json.get('mac')
            self.metadataValue: List[ContentManager.Player.MetadataValue] = [ContentManager.Player.MetadataValue(self, elem) for elem in json.get('metadataValue', [])]
            self.name: Optional[str] = json.get('name')
            self.numberOfDisplays: Optional[int] = json.get('numberOfDisplays')
            self.ownerWorkgroup: Optional[ContentManager.Workgroup] = self.cm.workgroups.get(owner_workgroup_id)
            self.pairingKey: Optional[str] = json.get('pairingKey')
            self.planDeliveryMethod: Optional[str] = json.get('planDeliveryMethod')
            self.planDeliveryPassword: Optional[str] = json.get('planDeliveryPassword')
            self.planDeliveryUsername: Optional[str] = json.get('planDeliveryUsername')
            self.playerDisplays: List[ContentManager.Player.Display] = [ContentManager.Player.Display(self, elem) for elem in json.get('playerDisplays', [])]
            self.playerId: Optional[str] = json.get('playerId')
            self.playerUrlOrHostName: Optional[str] = json.get('playerUrlOrHostName')
            self.playergroups: List[ContentManager.PlayerGroup] = get_list(json.get('playergroups'), self.cm.playergroups)
            self.pollingInterval: Optional[int] = json.get('pollingInterval')
            self.pollingUnit: Optional[str] = json.get('pollingUnit')
            self.previewPlayer: Optional[bool] = json.get('previewPlayer') #DEPRECATED
            self.readOnly: Optional[bool] = json.get('readOnly')
            self.requestLogs: Optional[bool] = json.get('requestLogs')
            self.sharedWorkgroups: List[ContentManager.Workgroup] = get_list(json.get('sharedWorkgroups'), self.cm.workgroups)
            # self.site: Optional[ContentManager.Site] = self.cm.sites.get(site_id)
            self.timezoneOffset: Optional[str] = json.get('timezoneOffset')
            self.type: Optional[str] = json.get('type')
            self.unusedFilesCache: Optional[int] = json.get('unusedFilesCache')
            self.usedPairingKey: Optional[str] = json.get('usedPairingKey')
            self.uuid: Optional[str] = json.get('uuid')
            self.workgroups: List[ContentManager.Workgroup] = get_list(json.get('workgroups'), self.cm.workgroups)

        def unpack_json_state(self, json: Dict[str, Any]):
            self.host: Optional[str] = json.get('host')
            self.ip: Optional[str] = json.get('ip')
            self.lastBooted: Optional[str] = json.get('lastBooted')
            self.lastBootedTimestamp: Optional[str] = json.get('lastBootedTimestamp')
            self.lastReported: Optional[str] = json.get('lastReported')
            self.lastReportedTimestamp: Optional[str] = json.get('lastReportedTimestamp')
            self.planState: Optional[str] = json.get('planState')
            self.releaseString: Optional[str] = json.get('releaseString')
            self.state: Optional[str] = json.get('state')

        def generate_uuid(self):
            params = {
                'ids': self.id
            }

            response = self.cm.request('post', '/storage', data=json.dumps(params))

            return response.get('value')

        def update_metadata(self, name: str, value: Any):
            if not name.startswith('Player.'):
                name = f"Player.{name}"

            metadata = self.cm.player_metadatas.get(name)

            if metadata is None:
                raise Exception(f'No metadata found with name {name}')

            if self.metadataValue is None:
                self.metadataValue = [ContentManager.Player.MetadataValue(self, {'value': value, 'playerMetadata': metadata.json()})]
            else:
                exists = False

                for i, v in enumerate(self.metadataValue):
                    if v.playerMetadata is None:
                        continue

                    if v.playerMetadata.name == name:
                        exists = True
                        if not value is None:
                            self.metadataValue[i].value = value

                if not exists:
                    self.metadataValue.append(ContentManager.Player.MetadataValue(self, {'value': value, 'playerMetadata': metadata.json()}))

        def save(self):
            self.cm.request('put', f'/players/{self.id}', data=json.dumps(self.json(update=True)), debug_key='update_player')

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()

            del data['cm']

            for name, use in kwargs.items():
                if name == "update" and use:
                    data = {k:v for k,v in data.items() if k in ['active', 'availableTargets', 'distributionServer', 'downloadThreads', 'enabled', 'id', 'lastModified', 'logLevel', 'mac', 'metadataValue', 'name', 'numberOfDisplays', 'overrideStatus', 'planDeliveryMethod', 'playerDisplays', 'pollingInterval', 'pollingUnit', 'previewPlayer', 'readOnly', 'requestLogs', 'timezoneOffset', 'type', 'unusedFilesCache', 'uuid', 'workgroups', 'ownerWorkgroup', 'bandwidthThrottlingWindows', 'limitDefaultBandwidth', 'playergroups', 'description']}

            for key in list(kwargs.keys()):
                if not "_" in key:
                    kwargs[f"player_{key}"] = kwargs.pop(key)

            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            own_workgroup_id = data.get('ownerWorkgroup', {}).get("id")

            if own_workgroup_id is None:
                return data
            else:
                data.pop('ownerWorkgroup', None)
                for i, elem in enumerate(data.get('workgroups', [])):
                    if elem.get('id') == own_workgroup_id:
                        data['workgroups'][i]['owner'] = True

            return data

        class Display:
            def __init__(self, player: ContentManager.Player, json: Optional[Dict[str, Any]]) -> None:
                json = json if not json is None else {}
                self.player = player
                self.unpack_json(json)

            def unpack_json(self, json:Dict[str,Any]) -> None:
                channel_id = get_id(json.get('channel'))

                self.channel: Optional[ContentManager.Channel] = self.player.cm.channels.get(channel_id)
                self.description: Optional[str] = json.get('description')
                self.id: Optional[int] = json.get('id')
                self.name: Optional[str] = json.get('name')
                self.screenCounter: Optional[int] = json.get('screenCounter')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['player']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class BandwidthThrottlingWindow:
            def __init__(self, player: ContentManager.Player, json: Optional[Dict[str, Any]]) -> None:
                json = json if not json is None else {}
                self.player = player
                self.unpack_json(json)

            def unpack_json(self, json:Dict[str,Any]) -> None:
                self.day: Optional[List[str]] = json.get('day')
                self.endTime: Optional[str] = json.get('endTime')
                self.id: Optional[int] = json.get('id')
                self.limit: Optional[int] = json.get('limit')
                self.order: Optional[int] = json.get('order')
                self.startTime: Optional[str] = json.get('startTime')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['player']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class FeatureLicense:
            def __init__(self, player: ContentManager.Player, json: Optional[Dict[str, Any]]) -> None:
                json = json if not json is None else {}
                self.player = player
                self.unpack_json(json)

            def unpack_json(self, json:Dict[str,Any]) -> None:
                self.alternateScheduleOptionsSupport: Optional[bool] = json.get('alternateScheduleOptionsSupport')
                self.customMonitorConfigs: Optional[bool] = json.get('customMonitorConfigs')
                self.deviceManagement: Optional[bool] = json.get('deviceManagement')
                self.html5Support: Optional[bool] = json.get('html5Support')
                self.imageSupport: Optional[bool] = json.get('imageSupport')
                self.maxChannel: Optional[int] = json.get('maxChannel')
                self.maxOutputs: Optional[int] = json.get('maxOutputs')
                self.maxPixel: Optional[int] = json.get('maxPixel')
                self.maxZone: Optional[int] = json.get('maxZone')
                self.playerPlaybackAuditLogsSupport: Optional[bool] = json.get('playerPlaybackAuditLogsSupport')
                self.scalaIntegrationAccess: Optional[bool] = json.get('scalaIntegrationAccess')
                self.scalaScriptSupport: Optional[bool] = json.get('scalaScriptSupport')
                self.statusMonitoring: Optional[str] = json.get('statusMonitoring')
                self.total: Optional[int] = json.get('total')
                self.triggersSupport: Optional[bool] = json.get('triggersSupport')
                self.type: Optional[str] = json.get('type')
                self.used: Optional[int] = json.get('used')
                self.videoSupport: Optional[bool] = json.get('videoSupport')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['player']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class MetadataValue:
            def __init__(self, player: ContentManager.Player, json: Optional[Dict[str, Any]]) -> None:
                self.player = player
                json = json if not json is None else {}
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                player_metadata_id = get_id(json.get('playerMetadata'))

                self.id: Optional[int] = json.get('id')
                self.playerMetadata: Optional[ContentManager.PlayerMetadata] = self.player.cm.player_metadatas.get(player_metadata_id)
                self.value: Optional[str] = json.get('value')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['player']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

    class PlayerList(MutableSequence[Player]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.Player]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/players')

            for elem in response.get('list', []):
                item = ContentManager.Player(self.cm, elem)
                item.unpack_json_state(self.cm.request('get', f'/players/{item.id}/state', debug_key="player_state"))

                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.Player]:
            if search is None:
                return None
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            logging.info(f'Player with {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.Player) -> None:
            self.__data.append(value)

    """ PLAYLIST """
    class Playlist:
        def __init__(self, cm: ContentManager, json: Dict[str, Any]) -> None:
            self.cm = cm
            self.media: List[ContentManager.Media] = []
            self.unpack_json(json)

        def unpack_json(self, json: Dict[str, Any]):
            created_by_id = get_id(json.get('createdBy'))
            modified_by_id = get_id(json.get('modifiedBy'))

            self.asSubPlaylistsCount: int = json.get('asSubPlaylistsCount', 0)
            self.campaignChannelsCount: Optional[int] = json.get('campaignChannelsCount')
            self.campaignMessagesCount: Optional[int] = json.get('campaignMessagesCount')
            self.campaignPlaylist: Optional[bool] = json.get('campaignPlaylist')
            self.categories: List[ContentManager.Category] = get_list(json.get('categories'), self.cm.categories)
            self.channelsCount: int = json.get('channelsCount', 0)
            self.controlledByAdManager: Optional[bool] = json.get('controlledByAdManager')
            self.createdBy: Optional[ContentManager.User] = self.cm.users.get(created_by_id)
            self.createdByName: Optional[str] = json.get('createdByName')
            self.createdDate: Optional[str] = json.get('createdDate')
            self.description: Optional[str] = json.get('description')
            self.durationCalculationCompleted: Optional[bool] = json.get('durationCalculationCompleted')
            self.enableSmartPlaylist: Optional[bool] = json.get('enableSmartPlaylist')
            self.extSourceDuration: Optional[int] = json.get('extSourceDuration')
            self.healthy: Optional[bool] = json.get('healthy')
            self.htmlDuration: Optional[int] = json.get('htmlDuration')
            self.id: Optional[int] = json.get('id')
            self.imageDuration: Optional[int] = json.get('imageDuration')
            self.itemCount: int = json.get('itemCount', 0)
            self.lastModified: Optional[str] = json.get('lastModified')
            self.maxDuration: Optional[int] = json.get('maxDuration')
            self.messagesCount: int = json.get('messagesCount', 0)
            self.minDuration: Optional[int] = json.get('minDuration')
            self.modifiedBy: Optional[ContentManager.User] = self.cm.users.get(modified_by_id)
            self.modifiedByName: Optional[str] = json.get('modifiedByName')
            self.name: Optional[str] = json.get('name')
            self.pickPolicy: Optional[str] = json.get('pickPolicy')
            self.playlistItems: List[ContentManager.Playlist.PlaylistItem] = [ContentManager.Playlist.PlaylistItem(self, elem) for elem in json.get('playlistItems', [])]
            self.playlistType: Optional[str] = json.get('playlistType')
            self.prettifyDuration: Optional[str] = json.get('prettifyDuration')
            self.priority: Optional[str] = json.get('priority')
            self.problemsCount: Optional[int] = json.get('problemsCount')
            self.readOnly: Optional[bool] = json.get('readOnly')
            self.shuffleNoRepeatType: Optional[str] = json.get('shuffleNoRepeatType')
            self.shuffleNoRepeatWithin: Optional[int] = json.get('shuffleNoRepeatWithin')
            self.thumbnailDownloadPath: Optional[str] = json.get('thumbnailDownloadPath')
            self.thumbnailDownloadPaths: ContentManager.Playlist.ThumbnailDownloadPaths = ContentManager.Playlist.ThumbnailDownloadPaths(self, json.get('thumbnailDownloadPaths'))
            self.transitionDuration: Optional[int] = json.get('transitionDuration')
            self.warningsCount: Optional[int] = json.get('warningsCount')
            self.workgroups: List[ContentManager.Workgroup] = get_list(json.get('workgroups'), self.cm.workgroups)

        def process(self, data: Union[int, ContentManager.Playlist], playlist_path: List[int] = []):
            if isinstance(data, int):
                playlist: Optional[ContentManager.Playlist] = self.cm.playlists.get(data)
                id = data
            else:
                playlist = data
                id = data.id
                if id is None:
                    raise Exception("ID cannot be None")

            if id in playlist_path:
                raise Exception(f"Playlistloop detected {playlist_path}")

            playlist_path.append(id)

            if not playlist is None:
                if playlist.playlistItems is None:
                    playlist_path.pop()
                    return

                for playlistItem in playlist.playlistItems:
                    if not playlistItem.media is None:
                        if not playlistItem.media in self.media:
                            self.media.append(playlistItem.media)

                    if not playlistItem.subplaylist is None:
                        self.process(playlistItem.subplaylist, playlist_path)

                playlist_path.pop()

        def get_media(self) -> List[ContentManager.Media]:
            if self.id is None:
                raise Exception("Object needs to have ID")

            self.process(self.id)

            return self.media

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']
            del data['media']

            for name, use in kwargs.items():
                #testing
                pass

            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

        class PlaylistItem:
            def __init__(self, playlist: ContentManager.Playlist, json: Optional[Dict[str, Any]]) -> None:
                json = json if not json is None else {}
                self.playlist = playlist
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                media_id = get_id(json.get('media'))
                sub_playlist_id = get_id(json.get('subplaylist'))

                self.audioDucking: Optional[bool] = json.get('audioDucking')
                self.auditItem: Optional[bool] = json.get('auditItem')
                self.conditions: List[ContentManager.Playlist.PlaylistItem.Condition] = [ContentManager.Playlist.PlaylistItem.Condition(self, elem) for elem in json.get('conditions', [])]
                self.disabled: Optional[bool] = json.get('disabled')
                self.duration: Optional[int] = json.get('duration')
                self.durationHoursSeconds: Optional[str] = json.get('durationHoursSeconds')
                self.endValidDate: Optional[str] = json.get('endValidDate')
                self.id: Optional[int] = json.get('id')
                self.inPoint: Optional[int] = json.get('inPoint')
                self.media: Optional[ContentManager.Media] = self.playlist.cm.media.get(media_id)
                self.meetAllConditions: Optional[bool] = json.get('meetAllConditions')
                self.options: List[ContentManager.Playlist.PlaylistItem.Option] = [ContentManager.Playlist.PlaylistItem.Option(self, elem) for elem in json.get('options', [])]
                self.outPoint: Optional[int] = json.get('outPoint')
                self.playFullscreen: Optional[bool] = json.get('playFullscreen')
                self.playlistItemType: Optional[str] = json.get('playlistItemType')
                self.prettifyInPoint: Optional[str] = json.get('prettifyInPoint')
                self.prettifyOutPoint: Optional[str] = json.get('prettifyOutPoint')
                self.sortOrder: Optional[int] = json.get('sortOrder')
                self.startValidDate: Optional[str] = json.get('startValidDate')
                self.status: Optional[List[str]] = json.get('status')
                self.subPlaylistPickPolicy: Optional[int] = json.get('subPlaylistPickPolicy')
                self.subplaylist: Optional[int] = sub_playlist_id
                self.timeSchedules: List[ContentManager.Playlist.PlaylistItem.Schedule] = [ContentManager.Playlist.PlaylistItem.Schedule(self, elem) for elem in json.get('timeSchedules', [])]
                self.useValidRange: Optional[bool] = json.get('useValidRange')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['playlist']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

            class Schedule:
                def __init__(self, playlistitem: ContentManager.Playlist.PlaylistItem, json: Dict[str, Any]) -> None:
                    self.playlistitem = playlistitem
                    self.unpack_json(json)

                def unpack_json(self, json: Dict[str, Any]):
                    self.days: Optional[List[str]] = json.get('days')
                    self.endTime: Optional[str] = json.get('endTime')
                    self.sortOrder: Optional[int] = json.get('sortOrder')
                    self.startTime: Optional[str] = json.get('startTime')

                def json(self, **kwargs: bool):
                    data = vars(self)

                    data = data.copy()


                    del data['playlistitem']

                    for name, use in kwargs.items():
                        #testing
                        pass

                    for k, v in data.items():
                        try:
                            if isinstance(data[k], list):
                                for i, elem in enumerate(data[k]):
                                    try:
                                        data[k][i] = elem.json(**kwargs)
                                    except Exception:
                                        continue
                            else:
                                data[k] = v.json(**kwargs)
                        except Exception:
                            continue

                    data = clean_data(data)

                    if data is None:
                        return data

                    return data

            class Option:
                def __init__(self, playlistitem: ContentManager.Playlist.PlaylistItem, json: Dict[str, Any]) -> None:
                    self.playlistitem = playlistitem
                    self.unpack_json(json)

                def unpack_json(self, json: Dict[str, Any]):
                    self.key: Optional[str] = json.get('key')
                    self.value: Optional[str] = json.get('value')

                def json(self, **kwargs: bool):
                    data = vars(self)

                    data = data.copy()


                    del data['playlistitem']

                    for name, use in kwargs.items():
                        #testing
                        pass

                    for k, v in data.items():
                        try:
                            if isinstance(data[k], list):
                                for i, elem in enumerate(data[k]):
                                    try:
                                        data[k][i] = elem.json(**kwargs)
                                    except Exception:
                                        continue
                            else:
                                data[k] = v.json(**kwargs)
                        except Exception:
                            continue

                    data = clean_data(data)

                    if data is None:
                        return data

                    return data

            class Condition:
                def __init__(self, playlistitem: ContentManager.Playlist.PlaylistItem, json: Dict[str, Any]) -> None:
                    self.playlistitem = playlistitem
                    self.unpack_json(json)

                def unpack_json(self, json: Dict[str, Any]):
                    self.id: Optional[int] = json.get('id')
                    self.type: Optional[str] = json.get('type')
                    self.comparator: Optional[str] = json.get('comparator')
                    self.value: Optional[str] = json.get('value')
                    self.sortOrder: Optional[int] = json.get('sortOrder')
                    self.metadata: Optional[int] = get_id(json.get('metadata'))

                def json(self, **kwargs: bool):
                    data = vars(self)

                    data = data.copy()


                    del data['playlistitem']

                    for name, use in kwargs.items():
                        #testing
                        pass

                    for k, v in data.items():
                        try:
                            if isinstance(data[k], list):
                                for i, elem in enumerate(data[k]):
                                    try:
                                        data[k][i] = elem.json(**kwargs)
                                    except Exception:
                                        continue
                            else:
                                data[k] = v.json(**kwargs)
                        except Exception:
                            continue

                    data = clean_data(data)

                    if data is None:
                        return data

                    return data

        class ThumbnailDownloadPaths:
            def __init__(self, playlist: ContentManager.Playlist,  json: Optional[Dict[str, Any]]) -> None:
                self.playlist = playlist
                json = json if not json is None else {}
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.extraSmall: Optional[str] = json.get('extraSmall')
                self.small: Optional[str] = json.get('small')
                self.mediumSmall: Optional[str] = json.get('mediumSmall')
                self.medium: Optional[str] = json.get('medium')
                self.large: Optional[str] = json.get('large')

                ### UNUSED BY FIRST
                self.custom: Optional[str] = json.get('custom')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['playlist']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

    class PlaylistList(MutableSequence[Playlist]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.Playlist]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/playlists/all')

            for elem in response.get('list', []):
                item = ContentManager.Playlist(self.cm, elem)
                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.Playlist]:
            if search is None:
                return None

            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                    if elem.name == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            logging.info(f'Playlist with {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.Playlist) -> None:
            self.__data.append(value)

    """ RESOURCE """
    class Resource:
        def __init__(self, cm: ContentManager, json: Dict[str, Any]) -> None:
            self.cm = cm
            self.unpack_json(json)

        def unpack_json(self, json: Dict[str, Any]):
            self.descritpion: Optional[str] = json.get('description')
            self.id: Optional[int] = json.get('id')
            self.implicitResources: Optional[List[str]] = json.get('implicitResources')
            self.name: Optional[str] = json.get('name')
            self.parentId: Optional[int] = json.get('parentId')
            self.sortOrder: Optional[int] = json.get('sortOrder')

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']

            for name, use in kwargs.items():
                #testing
                pass

            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

    class ResourceList(MutableSequence[Resource]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.Resource]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/roles/resources')

            for elem in response.get('resources', []):
                item = ContentManager.Resource(self.cm, elem)
                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.Resource]:
            if search is None:
                return None
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            logging.info(f'Resource {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.Resource) -> None:
            self.__data.append(value)

    """ ROLE """
    class Role:
        def __init__(self, cm: ContentManager, json: Dict[str, Any]) -> None:
            self.cm = cm
            self.unpack_json(json)

        def unpack_json(self, json: Dict[str, Any]):
            self.availableSeats: Optional[int] = json.get('availableSeats')
            self.id: Optional[int] = json.get('id')
            self.licenseRequirement: Optional[str] = json.get('licenseRequirement')
            self.name: Optional[str] = json.get('name')
            self.resources: List[ContentManager.Resource] = get_list(json.get('resources'), self.cm.resources)
            self.system: Optional[bool] = json.get('system')

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']

            for name, use in kwargs.items():
                #testing
                pass

            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

    class RoleList(MutableSequence[Role]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.Role]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/roles')

            for elem in response.get('list', []):
                item = ContentManager.Role(self.cm, elem)
                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.Role]:
            if search is None:
                return None
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            logging.info(f'Role with {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.Role) -> None:
            self.__data.append(value)

    """ TEMPLATE """
    class Template:
        def __init__(self, cm: ContentManager, data: Dict[str, Any]) -> None:
            self.cm = cm
            self.unpack_json(data)

        def unpack_json(self, json: Dict[str, Any]):
            modified_user_id = get_id(json.get('modifiedBy'))
            uploaded_user_id = get_id(json.get('uploadedBy'))

            self.approvalDetail: ContentManager.Template.ApprovalDetail = ContentManager.Template.ApprovalDetail(self, json.get('approvalDetail'))
            self.approvalStatus: Optional[str] = json.get('approvalStatus')
            self.archived: Optional[bool] = json.get('archived')
            self.audioDucking: Optional[bool] = json.get('audioDucking')
            self.campaignMedia: Optional[bool] = json.get('campaignMedia')
            self.categories: List[ContentManager.Category] = get_list(json.get('categories'), self.cm.categories)
            self.createdDate: Optional[str] = json.get('createdDate')
            self.downloadPath: Optional[str] = json.get('downloadPath')
            self.generatingThumbnail: Optional[bool] = json.get('generatingThumbnail')
            self.globalTemplateFields: List[ContentManager.Template.Field] = [ContentManager.Template.Field(self, elem) for elem in json.get('globalTemplateFields', [])]
            self.height: Optional[int] = json.get('height')
            self.id: Optional[int] = json.get('id')
            self.lastModified: Optional[str] = json.get('lastModified')
            self.length: Optional[int] = json.get('length')
            self.mediaId: Optional[int] = json.get('mediaId')
            self.mediaItemFiles: List[ContentManager.Template.ItemFile] = [ContentManager.Template.ItemFile(self, elem) for elem in json.get('mediaItemFiles', [])]
            self.mediaType: Optional[str] = json.get('mediaType')
            self.messagesCount: int = json.get('messagesCount', 0)
            self.modifiedBy: Optional[ContentManager.User] = self.cm.users.get(modified_user_id)
            self.name: Optional[str] = json.get('name')
            self.neverArchive: Optional[bool] = json.get('neverArchive')
            self.numberOfFields: int = json.get('numberOfFields', 0)
            self.numberOfFiles: int = json.get('numberOfFiles', 0)
            self.originalCreatedDate: Optional[str] = json.get('originalCreatedDate')
            self.path: Optional[str] = json.get('path')
            self.playFullscreen: Optional[bool] = json.get('playFullscreen')
            self.playlistsCount: int = json.get('playlistsCount', 0)
            self.prettifyDuration: Optional[str] = json.get('prettifyDuration')
            self.prettifyLength: Optional[str] = json.get('prettifyLength')
            self.prettifyType: Optional[str] = json.get('prettifyType')
            self.readOnly: Optional[bool] = json.get('readOnly')
            self.revision: Optional[int] = json.get('revision')
            self.startValidDate: Optional[str] = json.get('startValidDate')
            self.status: Optional[str] = json.get('status')
            self.templateFields: List[ContentManager.Template.Field] = [ContentManager.Template.Field(self, elem) for elem in json.get('templateFields', [])]
            self.templateVersion: Optional[int] = json.get('templateVersion')
            self.templatesCount: int = json.get('templatesCount', 0)
            self.thumbnailDownloadPaths: ContentManager.Template.ThumbnailDownloadPaths = ContentManager.Template.ThumbnailDownloadPaths(self, json.get('thumbnailDownloadPaths'))
            self.uploadType: Optional[str] = json.get('uploadType')
            self.uploadedBy: Optional[ContentManager.User] = self.cm.users.get(uploaded_user_id)
            self.validDateStatus: Optional[str] = json.get('validDateStatus')
            self.webDavPath: Optional[str] = json.get('webDavPath')
            self.width: Optional[int] = json.get('width')
            self.workgroups: List[ContentManager.Workgroup] = get_list(json.get('workgroups'), self.cm.workgroups)

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']

            for name, use in kwargs.items():
                #testing
                pass

            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

        class ThumbnailDownloadPaths:
            def __init__(self, template: ContentManager.Template,  json: Optional[Dict[str, Any]]) -> None:
                self.template = template
                json = json if not json is None else {}
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.extraSmall: Optional[str] = json.get('extraSmall')
                self.small: Optional[str] = json.get('small')
                self.mediumSmall: Optional[str] = json.get('mediumSmall')
                self.medium: Optional[str] = json.get('medium')
                self.large: Optional[str] = json.get('large')

                ### UNUSED BY FIRST
                self.custom: Optional[str] = json.get('custom')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['template']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class ApprovalDetail:
            def __init__(self, template: ContentManager.Template,  json: Optional[Dict[str, Any]]) -> None:
                self.template = template
                json = json if not json is None else {}
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.id: Optional[int] = json.get('id')
                self.approvalStatus: Optional[str] = json.get('approvalStatus')

                user_id = get_id(json.get('user'))
                self.user: Optional[ContentManager.User] = self.template.cm.users.get(user_id)

                to_approve_id = get_id(json.get('toApprove'))
                self.toApprove: Optional[ContentManager.User] = self.template.cm.users.get(to_approve_id)

                by_approve_id = get_id(json.get('approvedBy'))
                self.approvedBy: Optional[ContentManager.User] = self.template.cm.users.get(by_approve_id)

                self.messageText: Optional[str] = json.get('messageText')
                self.lastModified: Optional[str] = json.get('lastModified')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['template']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class ItemFile:
            def __init__(self, template: ContentManager.Template,  json: Dict[str, Any]) -> None:
                self.template = template
                json = json if not json is None else {}
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.id: Optional[int] = json.get('id')
                self.filename: Optional[str] = json.get('filename')
                self.size: Optional[int] = json.get('size')
                self.prettifySize: Optional[str] = json.get('prettifySize')
                self.uploadDate: Optional[str] = json.get('uploadDate')
                self.version: Optional[int] = json.get('version')
                self.downloadPath: Optional[str] = json.get('downloadPath')
                self.originalFilename: Optional[str] = json.get('originalFilename')
                self.status: Optional[str] = json.get('status')
                self.uploadedBy: Optional[str] = json.get('uploadedBy')
                self.md5: Optional[str] = json.get('md5')

                self.thumbnailDownloadPaths: ContentManager.Template.ItemFile.ThumbnailDownloadPaths = ContentManager.Template.ItemFile.ThumbnailDownloadPaths(self, json.get('thumbnailDownloadPaths'))

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['template']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

            class ThumbnailDownloadPaths:
                def __init__(self, itemfile: ContentManager.Template.ItemFile,  json: Optional[Dict[str, Any]]) -> None:
                    self.itemfile = itemfile
                    json = json if not json is None else {}
                    self.unpack_json(json)

                def unpack_json(self, json: Dict[str, Any]):
                    self.extraSmall: Optional[str] = json.get('extraSmall')
                    self.small: Optional[str] = json.get('small')
                    self.mediumSmall: Optional[str] = json.get('mediumSmall')
                    self.medium: Optional[str] = json.get('medium')
                    self.large: Optional[str] = json.get('large')

                    ### UNUSED BY FIRST
                    self.custom: Optional[str] = json.get('custom')

                def json(self, **kwargs: bool):
                    data = vars(self)

                    data = data.copy()


                    del data['itemfile']

                    for name, use in kwargs.items():
                        #testing
                        pass

                    for k, v in data.items():
                        try:
                            if isinstance(data[k], list):
                                for i, elem in enumerate(data[k]):
                                    try:
                                        data[k][i] = elem.json(**kwargs)
                                    except Exception:
                                        continue
                            else:
                                data[k] = v.json(**kwargs)
                        except Exception:
                            continue

                    data = clean_data(data)

                    if data is None:
                        return data

                    return data

        class Field:
            def __init__(self, template: ContentManager.Template,  json: Optional[Dict[str, Any]]) -> None:
                self.template = template
                json = json if not json is None else {}
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.id: Optional[int] = json.get('id')
                self.name: Optional[str] = json.get('name')
                self.displayName: Optional[str] = json.get('displayName')
                self.value: Optional[str] = json.get('value')
                self.required: Optional[bool] = json.get('required')
                self.type: Optional[str] = json.get('type')
                self.editable: Optional[bool] = json.get('editable')
                self.maxCharacters: Optional[int] = json.get('maxCharacters')
                self.maxLines: Optional[int] = json.get('maxLines')
                self.useDefault: Optional[bool] = json.get('useDefault')

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['template']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

        class Page:
            def __init__(self, template: ContentManager.Template,  json: Optional[Dict[str, Any]]) -> None:
                self.template = template
                json = json if not json is None else {}
                self.unpack_json(json)

            def unpack_json(self, json: Dict[str, Any]):
                self.id: Optional[int] = json.get('id')
                self.name: Optional[str] = json.get('name')
                self.editable: Optional[bool] = json.get('editable')
                self.thumbnailPageEnabled: Optional[bool] = json.get('thumbnailPageEnabled')
                self.order: Optional[int] = json.get('order')
                self.thumbnailPageNo: Optional[int] = json.get('thumbnailPageNo')

                self.thumbnailDownloadPaths: ContentManager.Template.Page.ThumbnailDownloadPaths = ContentManager.Template.Page.ThumbnailDownloadPaths(self, json.get('thumbnailDownloadPaths'))
                self.templateFields: List[ContentManager.Template.Page.Field] = [ContentManager.Template.Page.Field(self, elem) for elem in json.get('templateFields', [])]
                self.idents: List[ContentManager.Template.Page.Ident] = [ContentManager.Template.Page.Ident(self, elem) for elem in json.get('idents', [])]

            def json(self, **kwargs: bool):
                data = vars(self)

                data = data.copy()


                del data['template']

                for name, use in kwargs.items():
                    #testing
                    pass

                for k, v in data.items():
                    try:
                        if isinstance(data[k], list):
                            for i, elem in enumerate(data[k]):
                                try:
                                    data[k][i] = elem.json(**kwargs)
                                except Exception:
                                    continue
                        else:
                            data[k] = v.json(**kwargs)
                    except Exception:
                        continue

                data = clean_data(data)

                if data is None:
                    return data

                return data

            class ThumbnailDownloadPaths:
                def __init__(self, page: ContentManager.Template.Page,  json: Optional[Dict[str, Any]]) -> None:
                    self.page = page
                    json = json if not json is None else {}
                    self.unpack_json(json)

                def unpack_json(self, json: Dict[str, Any]):
                    self.extraSmall: Optional[str] = json.get('extraSmall')
                    self.small: Optional[str] = json.get('small')
                    self.mediumSmall: Optional[str] = json.get('mediumSmall')
                    self.medium: Optional[str] = json.get('medium')
                    self.large: Optional[str] = json.get('large')

                    ### UNUSED BY FIRST
                    self.custom: Optional[str] = json.get('custom')

                def json(self, **kwargs: bool):
                    data = vars(self)

                    data = data.copy()


                    del data['page']

                    for name, use in kwargs.items():
                        #testing
                        pass

                    for k, v in data.items():
                        try:
                            if isinstance(data[k], list):
                                for i, elem in enumerate(data[k]):
                                    try:
                                        data[k][i] = elem.json(**kwargs)
                                    except Exception:
                                        continue
                            else:
                                data[k] = v.json(**kwargs)
                        except Exception:
                            continue

                    data = clean_data(data)

                    if data is None:
                        return data

                    return data

            class Field:
                def __init__(self, page: ContentManager.Template.Page,  json: Optional[Dict[str, Any]]) -> None:
                    self.page = page
                    json = json if not json is None else {}
                    self.unpack_json(json)

                def unpack_json(self, json: Dict[str, Any]):
                    self.id: Optional[int] = json.get('id')
                    self.name: Optional[str] = json.get('name')
                    self.displayName: Optional[str] = json.get('displayName')
                    self.value: Optional[str] = json.get('value')
                    self.required: Optional[bool] = json.get('required')
                    self.type: Optional[str] = json.get('type')
                    self.editable: Optional[bool] = json.get('editable')
                    self.maxCharacters: Optional[int] = json.get('maxCharacters')
                    self.maxLines: Optional[int] = json.get('maxLines')
                    self.useDefault: Optional[bool] = json.get('useDefault')

                def json(self, **kwargs: bool):
                    data = vars(self)

                    data = data.copy()


                    del data['page']

                    for name, use in kwargs.items():
                        #testing
                        pass

                    for k, v in data.items():
                        try:
                            if isinstance(data[k], list):
                                for i, elem in enumerate(data[k]):
                                    try:
                                        data[k][i] = elem.json(**kwargs)
                                    except Exception:
                                        continue
                            else:
                                data[k] = v.json(**kwargs)
                        except Exception:
                            continue

                    data = clean_data(data)

                    if data is None:
                        return data

                    return data

            class Ident:
                def __init__(self, page: ContentManager.Template.Page,  json: Optional[Dict[str, Any]]) -> None:
                    self.page = page
                    json = json if not json is None else {}
                    self.unpack_json(json)

                def unpack_json(self, json: Dict[str, Any]):
                    self.id: Optional[int] = json.get('id')
                    self.label: Optional[str] = json.get('label')
                    self.languageCode: Optional[str] = json.get('languageCode')
                    self.description: Optional[str] = json.get('description')

                def json(self, **kwargs: bool):
                    data = vars(self)

                    data = data.copy()


                    del data['page']

                    for name, use in kwargs.items():
                        #testing
                        pass

                    for k, v in data.items():
                        try:
                            if isinstance(data[k], list):
                                for i, elem in enumerate(data[k]):
                                    try:
                                        data[k][i] = elem.json(**kwargs)
                                    except Exception:
                                        continue
                            else:
                                data[k] = v.json(**kwargs)
                        except Exception:
                            continue

                    data = clean_data(data)

                    if data is None:
                        return data

                    return data

    class TemplateList(MutableSequence[Template]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.Template]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/templates')

            for elem in response.get('list', []):
                item = ContentManager.Template(self.cm, elem)
                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.Template]:
            if search is None:
                return None
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

            logging.info(f'Template with {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.Template) -> None:
            self.__data.append(value)

    """ USER """
    class User:
        def __init__(self, cm: ContentManager, data: Dict[str, Any]) -> None:
            self.cm = cm
            self.unpack_json(data)

        def unpack_json(self, json: Dict[str, Any]):
            self.authenticationMethod: Optional[str] = json.get('auhtenticationMethod')
            self.canChangePassword: Optional[bool] = json.get('canChangePassword')
            self.dateFormat: Optional[str] = json.get('dateFormat')
            self.emailaddress: Optional[str] = json.get('emailaddress')
            self.enabled: Optional[bool] = json.get('enabled')
            self.firstname: Optional[str] = json.get('firstname')
            self.forcePasswordChange: Optional[bool] = json.get('forcePasswordChange')
            self.id: Optional[int] = json.get('id')
            self.isAutoMediaApprover: Optional[bool] = json.get('isAutoMediaApprover')
            self.isAutoMessageApprover: Optional[bool] = json.get('isAutoMessageApprover')
            self.isSuperAdministrator: Optional[bool] = json.get('isSuperAdministrator')
            self.isWebserviceUser: Optional[bool] = json.get('isWebserviceUser')
            self.language: Optional[str] = json.get('language')
            self.languageCode: Optional[str] = json.get('languageCode')
            self.lastLogin: Optional[str] = json.get('lastLogin')
            self.lastname: Optional[str] = json.get('lastname')
            self.name: Optional[str] = json.get('name')
            self.oldPassword: Optional[str] = json.get('oldPassword')
            self.password: Optional[str] = json.get('password')
            self.passwordLastChanged: Optional[str] = json.get('passwordLastChanged')
            self.receiveApprovalEmails: Optional[bool] = json.get('receiveApprovalEmails')
            self.receiveEmailAlerts: Optional[bool] = json.get('receiveEmailAlerts')
            self.roles: List[ContentManager.Role] = get_list(json.get('roles'), self.cm.roles)
            self.theme: Optional[str] = json.get('theme')
            self.timeFormat: Optional[str] = json.get('timeFormat')
            self.userAccountWorkgroups: List[ContentManager.Workgroup] = get_list(json.get('userAccountWorkgroups'), self.cm.workgroups)
            self.username: Optional[str] = json.get('username')
            self.workgroup: Optional[int] = get_id(json.get('workgroup')) #DEPRECATED
            self.workgroups: List[ContentManager.Workgroup] = get_list(json.get('workgroups'), self.cm.workgroups)

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']

            for name, use in kwargs.items():
                #testing
                pass

            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

    class UserList(MutableSequence[User]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.User]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/users')

            for elem in response.get('list', []):
                item = ContentManager.User(self.cm, elem)
                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.User]:
            if search is None:
                return None
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.username == search:
                        return elem

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.username == search:
                        return elem

            logging.info(f'User with {search} not found')
            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.User) -> None:
            self.__data.append(value)

    """ WORKGROUP """
    class Workgroup:
        def __init__(self, cm: ContentManager,  data: Optional[Dict[str, Any]]) -> None:
            self.cm = cm
            data = data if not data is None else {}
            self.unpack_json(data)

        def unpack_json(self, json: Dict[str, Any]):
            self.children: List[ContentManager.Workgroup] = [ContentManager.Workgroup(self.cm, elem) for elem in json.get('children', [])]
            self.description: Optional[str] = json.get('description')
            self.id: Optional[int] = json.get('id')
            self.name: Optional[str] = json.get('name')
            self.owner: Optional[bool] = json.get('owner')
            self.parentId: Optional[int] = json.get('parentId')
            self.parentName: Optional[str] = json.get('parentName')
            self.userCount: Optional[int] = json.get('userCount')

        def json(self, **kwargs: bool):
            data = vars(self)

            data = data.copy()


            del data['cm']

            for name, use in kwargs.items():
                if name == 'player_update' and use:
                    data = {k:v for k,v in data.items() if k in ['id']}

            for k, v in data.items():
                try:
                    if isinstance(data[k], list):
                        for i, elem in enumerate(data[k]):
                            try:
                                data[k][i] = elem.json(**kwargs)
                            except Exception:
                                continue
                    else:
                        data[k] = v.json(**kwargs)
                except Exception:
                    continue

            data = clean_data(data)

            if data is None:
                return data

            return data

    class WorkgroupList(MutableSequence[Workgroup]):
        def __init__(self, cm: ContentManager, init_list: Optional[List[ContentManager.Workgroup]] = None) -> None:
            super().__init__()
            self.cm = cm

            if init_list is None:
                self.__get_data()
            else:
                self.__data = init_list

        def __get_data(self):
            response: Dict[str, Any] = self.cm.request('get', '/workgroups')

            for elem in response.get('list', []):
                item = ContentManager.Workgroup(self.cm, elem)
                self.__data.append(item)

        def get(self, search: Union[int, str, None]) -> Optional[ContentManager.Workgroup]:
            if search is None:
                return None

            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

                temp = search_children(search, elem.children, "id", "name", "children")

                if not temp is None:
                    return temp

            self.__get_data()

            for elem in self.__data:
                if isinstance(search, int):
                    if elem.id == search:
                        return elem
                else:
                    if elem.name == search:
                        return elem

                temp = search_children(search, elem.children, "id", "name", "children")

                if not temp is None:
                    return temp

            logging.info(f'Workgroup with {search} nof found')

            return None

        def __len__(self) -> int:
            return len(self.__data)

        def __iter__(self):
            if len(self.__data) == 0:
                self.__get_data()

            for elem in self.__data:
                yield elem

        def __getitem__(self, i: Union[slice, int]):
            if isinstance(i, slice):
                return self.__class__(self.cm, self.__data[i])
            else:
                return self.__data[i]

        def __delitem__(self, i: int):
            del self.__data[i]

        def __setitem__(self, i: int, value):
            self.__data[i] = value

        def insert(self, i: int, value) -> None:
            self.__data.insert(i, value)

        def append(self, value: ContentManager.Workgroup) -> None:
            self.__data.append(value)

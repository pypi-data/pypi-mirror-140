import uuid
from typing import (
    Optional,
    Any,
    Union,
    List,
    Tuple,
    Set,
)
from urllib.parse import urlparse, urlencode

import requests

from .enum import Permissions
from .exceptions import MisskeyMiAuthFailedException


class MiAuth:
    """Misskey Authentication Class

    Args:
        address (str): Instance address.
        You can also include the URL protocol.
        If not specified, it will be automatically
        recognized as :code:`https`.

        session_id (:obj:`uuid.UUID` or :obj:`str`, optional): Session ID
        for performing MiAuth. If not specified, it will be set automatically.

        name (:obj:`str`, optional): App name.

        icon (:obj:`str`, optional): The URL of the icon.

        callback (:obj:`str`, optional): App callback URL.

        permission (:obj:`list` of :obj:`str`, optional): The permissions
        that the app can use. You can specify an enumeration of Permissions.

        session (:obj:`requests.Session`, optional): If you have prepared the
        :obj:`requests.Session` class yourself, you can assign it here.
        Normally you do not need to specify it.
    """
    __DEFAULT_ADDRESS: str = 'https://misskey.io'

    __address: str
    __scheme: str
    __session_id: Union[uuid.UUID, str]
    __session: requests.Session

    __name: str
    __icon: Optional[str] = None
    __callback: Optional[str] = None
    __token: Optional[str] = None
    __permission: Union[
            List[Union[Permissions, str]],
            Tuple[Union[Permissions, None]],
            Set[Permissions],
            None,
    ] = None
    timeout: Optional[Any] = 15.0

    @property
    def address(self) -> str:
        """Misskey instance address for MiAuth. Cannot be edited.
        """
        return self.__address

    @property
    def name(self) -> str:
        """App name.

        It can be changed by assignment.
        """
        return self.__name

    @name.setter
    def name(self, val: str):
        self.__name = val

    @property
    def icon(self) -> Optional[str]:
        """The URL of the icon.

        It can be changed by assignment.

        If using :code:`del`, :code:`icon` will be :code:`None`.
        """
        return self.__icon

    @icon.setter
    def icon(self, val: str):
        self.__icon = val

    @icon.deleter
    def icon(self):
        self.__icon = None

    @property
    def callback(self) -> Optional[str]:
        """App callback URL.

        It can be changed by assignment.

        If using :code:`del`, :code:`icon` will be :code:`None`.
        """
        return self.__callback

    @callback.setter
    def callback(self, val: str):
        self.__callback = val

    @callback.deleter
    def callback(self):
        self.__callback = None

    @property
    def session_id(self) -> Union[
        uuid.UUID,
        str,
    ]:
        """Session ID for performing MiAuth. Cannot be edited.
        """
        return self.__session_id

    @property
    def permission(self) -> Union[
        List[Union[Permissions, str, None]],
        Tuple[Union[Permissions, None]],
        Set[Permissions],
        None,
    ]:
        """The permissions that the app can use.
        """
        return self.__permission

    @permission.setter
    def permission(self, val: Union[
        List[Union[Permissions, str, None]],
        Tuple[Union[Permissions, None]],
        Set[Permissions],
        None,
    ]):
        if type(val) is list:
            for index, v in enumerate(val):
                if type(v) is str:
                    self.__permission[index] = Permissions(v)
        else:
            self.__permission = val

    @property
    def token(self) -> Optional[str]:
        """Contains the token authenticated by MiAuth.
        If not authenticated, :code:`None` will be returned.
        """
        return self.__token

    @property
    def __endpoint(self):
        return f'{self.__scheme}://{self.__address}'

    def __init__(
        self,
        address: str = __DEFAULT_ADDRESS,
        session_id: Union[uuid.UUID, str, None] = None,
        name: str = 'Misskey.py',
        icon: Optional[str] = None,
        callback: Optional[str] = None,
        permission: Union[
            List[Union[Permissions, str, None]],
            Tuple[Union[Permissions, None]],
            Set[Union[Permissions, None]],
            None,
        ] = None,
        session: Optional[requests.Session] = None,
    ):
        parse_res = urlparse(address)

        if parse_res.scheme == '':
            parse_res = urlparse(f'https://{address}')

        self.__address = str(parse_res.netloc)
        self.__scheme = str(parse_res.scheme)

        if session is None:
            session = requests.Session()
        self.__session = session

        if permission is None:
            self.__permission = [pe.value for pe in Permissions]
        else:
            self.__permission = permission

        if type(self.__permission) is list:
            for index, val in enumerate(self.__permission):
                if type(val) is str:
                    self.__permission[index] = Permissions(val)

        if session_id is None:
            self.__session_id = uuid.uuid4()
        else:
            self.__session_id = session_id

        self.__name = name
        self.__icon = icon
        self.__callback = callback

    def generate_url(self) -> str:
        """Create a URL for your end user.

        Returns:
            str: The URL for the end user is returned.
            Instruct the end user to open it in a web browser or the like.
        """
        url_params = {
            'name': self.__name,
            'permission': ','.join(
                str(perm.value) for perm in self.__permission
            ),
        }
        if self.__icon is not None:
            url_params['icon'] = self.__icon
        if self.__callback is not None:
            url_params['callback'] = self.__callback

        return (
            f'{self.__endpoint}/miauth/{str(self.__session_id)}'
            f'?{urlencode(url_params)}'
        )

    def check(self) -> str:
        """Validate MiAuth authentication.

        Returns:
            str: If the authentication is successful,
            a MiAuth token will be returned.

        Note:
            The token obtained by this method is also assigned
            to the property :code:`token`.

        Raises:
            MisskeyMiAuthFailedException: Raise if MiAuth authentication fails.
        """
        res = self.__session.post(
            f'{self.__endpoint}/api/miauth/{str(self.__session_id)}/check',
            allow_redirects=False,
            timeout=self.timeout,
        )
        res.raise_for_status()
        res_json: dict = res.json()
        if not res_json.get('ok', False):
            raise MisskeyMiAuthFailedException()

        self.__token = res_json['token']
        return self.__token

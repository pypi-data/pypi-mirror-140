"""
MIT License

Copyright (c) 2022-present Scrumpy (Jay)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import aiohttp
from typing import (
    Union,
)

from .variables import (
    API_URL,
    VALID_SFW_REQUESTS,
    VALID_NSFW_REQUESTS,
)
from .errors import (
    InvalidCategoryProvided,
)

class Waifu:
    """
    Represents a way to interact with the waifu.pics API.
    """

    def __init__(self):
        self._session = None

    @property
    def _client_session(self) -> aiohttp.ClientSession:
        # Returns the aiohttp.ClientSession() value, creating a new one if None/closed.
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def _request(self, category: str, nsfw: bool=False, exclude: list=None) -> str:
        # Returns the data from the WaifuPics API (when many=False).
        exlude = exclude or [] # If None = [], else = exclude
        type_parameter = 'nsfw' if nsfw else 'sfw'
        json_request_headers = {"exclude": exclude}
        session = self._client_session
        async with session.get(f'{API_URL}/{type_parameter}/{category}', json=json_request_headers) as request:
            request.raise_for_status() # Raising an aiohttp error if status code not 2xx
            json_body = await request.json()
            return json_body['url']

    async def _request_many(self, category: str, nsfw: bool=False, exclude: list=None) -> list:
        # Returns the data from the WaifuPics API (when many=True).
        exlude = exclude or [] # If None = [], else = exclude
        type_parameter = 'nsfw' if nsfw else 'sfw'
        json_request_headers = {"exclude": exclude}
        session = self._client_session
        # Many requires a post instead of get
        async with session.post(f'{API_URL}/many/{type_parameter}/{category}', json=json_request_headers) as request:
            request.raise_for_status() # Raising an aiohttp error if status code not 2xx
            json_body = await request.json()
            return json_body['files'] # Returning a list of files

    async def sfw(self, category: str, many: bool=False, exclude: list=None) -> Union[str,list]:
        """Request a SFW image from the waifu.pics API.

        Args:
            category (:obj:`str`): What category of image do you want to request.
            many (:obj:`bool`, optional): Do you want to recieve 30 images instead of one?
            exclude (:obj:`list`, optional): Image URLs to NOT recieve from the API.

        Returns:
            str: An image URL of the requested type.
        """
        exlude = exclude or [] # If None = [], else = exclude
        if category.lower() not in VALID_SFW_REQUESTS: 
            raise InvalidCategoryProvided(f"Invalid SFW category, must be one of: {VALID_SFW_REQUESTS}")
        elif many:
            return await self._request_many(category=category, nsfw=False, exclude=exclude)
        
        return await self._request(category=category, nsfw=False, exclude=exclude)
        
    async def nsfw(self, category: str, many: bool=False, exclude: list=None) -> Union[str,list]:
        """Request a NSFW image from the waifu.pics API.

        Args:
            category (:obj:`str`): What category of image do you want to request.
            many (:obj:`bool`, optional): Do you want to recieve 30 images instead of one?
            exclude (:obj:`list`, optional): Image URLs to NOT recieve from the API.

        Returns:
            str: An image URL of the requested type.
        """
        exlude = exclude or [] # If None = [], else = exclude
        if category.lower() not in VALID_NSFW_REQUESTS: 
            raise InvalidCategoryProvided(f"Invalid NSFW category, must be one of: {VALID_NSFW_REQUESTS}")
        elif many:
            return await self._request_many(category=category, nsfw=True, exclude=exclude)
        
        return await self._request(category=category, nsfw=True, exclude=exclude)
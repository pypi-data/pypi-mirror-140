import aiohttp

from .._data.errors import RequestReturnedException
from .._data.typehints import CreateFlightSchema

BASE_URL = "https://roavflights.com/openapi"


class AsyncLandonApiWrapper:
    def __init__(self, api_key: str, session: aiohttp.ClientSession = None):
        self.body = {"apikey": api_key}

        self.session = session

    async def make_request(self, method: str, url, options: dict):
        if not self.session:
            match method:
                case "GET":
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, json=options) as req:
                            return req
                case "POST":
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, json=options) as req:
                            return req
        else:
            match method:
                case "GET":
                    req = await self.session.get(url, json=options)
                    return req
                case "POST":
                    req = await self.session.post(url, json=options)
                    return req

    async def get_flights(self):
        req = await self.make_request("GET", BASE_URL + "/flights/get", self.body)
        json_data = await req.json()

        if req.ok and json_data:
            return json_data['flights']
        else:
            raise RequestReturnedException(json_data)

    async def create_flight(self, options: CreateFlightSchema):
        body = dict(self.body, **options)

        req = await self.make_request("POST", BASE_URL + "/flights/create", body)
        json_data = await req.json()

        if req.ok and json_data:
            return json_data
        else:
            raise RequestReturnedException(json_data)

    async def delete_flight(self, flightID: str):
        body = dict(self.body, **{"flightID": flightID})

        req = await self.make_request("POST", BASE_URL + "/flights/delete", body)
        json_data = await req.json()

        if req.ok and json_data:
            return json_data
        else:
            return RequestReturnedException(json_data)

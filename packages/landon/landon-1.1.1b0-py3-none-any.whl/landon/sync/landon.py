import requests

from typing import TypedDict


class CreateFlightSchema(TypedDict):
    flightnumber: str
    aircraft: str
    departure_airport: str
    arrival_airport: str
    game_url: str
    date: str
    time: str
    roavhub_ping: bool


class RequestReturnedException(Exception):
    pass

BASE_URL = "https://roavflights.com/openapi"



class LandonApiWrapper:
    def __init__(self, api_key: str):
        self.body = {"apikey": api_key}

    def get_flights(self):
        req = requests.get(BASE_URL + "/flights/get", json=self.body)
        json_data = req.json()

        if req.ok and json_data:
            return json_data['flights']
        else:
            raise RequestReturnedException(json_data)

    def create_flight(self, options: CreateFlightSchema):
        body = dict(self.body, **options)

        req = requests.post(BASE_URL + "/flights/create", json=body)
        json_data = req.json()

        if req.ok and json_data:
            return json_data
        else:
            raise RequestReturnedException(json_data)

    def delete_flight(self, flightID: str):
        body = dict(self.body, **{"flightID": flightID})

        req = requests.post(BASE_URL + "/flights/delete", json=body)
        json_data = req.json()

        if req.ok and json_data:
            return json_data
        else:
            return RequestReturnedException(json_data)

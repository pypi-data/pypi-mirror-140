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

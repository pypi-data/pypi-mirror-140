from __future__ import annotations


from dataclasses import dataclass
from .const import STREET_ID_DICT
import enum
import requests
import datetime
import aiohttp
import asyncio

@dataclass
class BESTBottropGarbageCollectionDates:
    """ Class for managing connection and data to the BEST Bottrop garbage collection dates"""

    trash_types_json : list[dict] = ""
    HTTPSession : aiohttp.ClientSession() = None

    def _get_name_for_id(self, x, json):
        for i in json:
            if i.get("id") == x:
                return i.get("name")
        return x

    def _today_or_later(self, x):
        # Check and return only if the date in the JSON is today or later
        xday, xmonth, xyear = x.get("formattedDate").split(".")
        xdate = datetime.date(int(xyear), int(xmonth), int(xday))

        if xdate >= datetime.datetime.today().date():
            return x;
        else: return "";

    async def load_trash_types (self):
        # Load the trashtypes
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://www.best-bottrop.de/api/trashtype') as trash_types_response:
                    self.trash_types_json = await trash_types_response.json()
        except aiohttp.ClientError as e:
            print ("Could not load dates! Exception: {0}".format(e))
            raise e
            return ""

    def get_street_ids(self):
        return STREET_ID_DICT

    async def get_dates_as_json(self, street, number) -> list[dict]:
        # Get the BEST street id code for a given street
        street_code = STREET_ID_DICT.get(street)

        dates_json = ""

        if (street_code != None and self.trash_types_json != None):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get('https://www.best-bottrop.de/api/street/{0}/house/{1}/collection'.format(street_code, number)) as dates:
                        dates_json = await dates.json()
                        dates_json = list(filter(self._today_or_later, dates_json))
            except aiohttp.ClientError as e:
                print ("Could not load dates! Exception: {0}".format(e))
                raise e

            for date_item in dates_json:
                date_item.update({"trashType": self._get_name_for_id(date_item.get("trashType"), self.trash_types_json)})

        return dates_json
        
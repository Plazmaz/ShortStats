import base64

import requests

ENDPOINT_FMT = '{}{}'

class BitlyAPI(object):
    def __init__(self, token, base_url='https://api-ssl.bitly.com/v3'):
        self.base_url = base_url
        self.access_token = token
        self.auth_headers = {
            'Authorization': 'Bearer {}'.format(token)
        }

    def _endpoint_uri(self, endpoint):
        if endpoint[0] != '/':
            endpoint = '/' + endpoint

        return ENDPOINT_FMT.format(self.base_url, endpoint)

    def get(self, endpoint, params=None):
        params['access_token'] = self.access_token
        result = requests.get(url=self._endpoint_uri(endpoint), params=params, headers=self.auth_headers).json()
        if result.get('status_code') != 200:
            raise RuntimeError('Encountered error when retrieving data: {}'.format(result.get('status_txt')))
        return result

    def post(self, endpoint, params):
        result = requests.post(url=self._endpoint_uri(endpoint), data=params, headers=self.auth_headers).json()
        if result.get('status_code') != 200:
            raise RuntimeError('Encountered error when retrieving data: {}'.format(result.get('status_txt')))
        return result

    def get_countries(self, link, unit="day", units=-1, size=1000, unit_reference_ts=None):
        """
        https://dev.bitly.com/link_metrics.html#v3_link_countries
        Returns metrics about the countries referring click traffic to a single Bitlink.
        Response structure:
        ```
        {
          "data": {
            "countries": [
              {
                "clicks": Number,
                "country": String (ISO 3166-1 alpha-2 "US", "GB", etc)
              }
            ],
            "tz_offset": Number,
            "unit": str ("minute" "hour" "day" "week" "month"),
            "units": Number
          },
          "status_code": 200,
          "status_txt": "OK"
        }
        ```

        :param link: A Bitlink made of the domain and hash (bitly.com/example)
        :param unit: A unit of time ("minute" "hour" "day" "week" "month")
        :param units: An integer representing the time units to query data for. pass -1 to return all units of time.
        :param size: The quantity of items to be be returned (1..1000)
        :param unit_reference_ts: An ISO-8601 timestamp, indicating the most recent time for which to pull metrics. Will default to current time.
        """
        endpoint = '/link/countries'

        # Generate params
        params = {
            'link': link,
            'timezone': 0,
            'unit': unit,
            'units': units,
            'size': size
        }
        if unit_reference_ts:
            params['unit_reference_ts'] = unit_reference_ts
        return self.get(endpoint, params)

    def get_referrers(self, link, unit="day", units=-1, size=1000, unit_reference_ts=None):
        """
        https://dev.bitly.com/link_metrics.html#v3_link_referrers
        Returns metrics about the pages referring click traffic to a single Bitlink.
        This will get a list of clicks by referring page/domain, or "direct" if no referrer is set
        Response structure:
        ```
        {
          "data": {
            "referrers": [
              {
                "clicks": Number,
                "referrer": str ("direct" or "example.com")
              }
            ],
            "tz_offset": Number,
            "unit": str ("minute" "hour" "day" "week" "month"),
            "units": Number
          },
          "status_code": 200,
          "status_txt": "OK"
        }
        ```

        :param link: A Bitlink made of the domain and hash (bitly.com/example)
        :param unit: A unit of time ("minute" "hour" "day" "week" "month")
        :param units: An integer representing the time units to query data for. pass -1 to return all units of time.
        :param size: The quantity of items to be be returned (1..1000)
        :param unit_reference_ts: An ISO-8601 timestamp, indicating the most recent time for which to pull metrics. Will default to current time.
        """
        endpoint = '/link/referrers'
        # Generate params
        params = {
            'link': link,
            'timezone': 0,
            'unit': unit,
            'units': units,
            'size': size
        }
        if unit_reference_ts:
            params['unit_reference_ts'] = unit_reference_ts
        return self.get(endpoint, params)

    def get_clicks(self, link, unit="day", units=-1, size=1000, rollup=False, unit_reference_ts=None):
        """
        https://dev.bitly.com/link_metrics.html#v3_link_clicks
        Get Clicks Summary for a Bitlink
        This will return The click counts for a specified Bitlink. This rolls up all the data into a single field of clicks.
        Response structure:
        ```
        {
          "data": {
            "link_clicks": Number,
            "tz_offset": Number,
            "unit": str ("minute" "hour" "day" "week" "month"),
            "unit_reference_ts": Number (Timestamp),
            "units": Number
          },
          "status_code": 200,
          "status_txt": "OK"
        }
        ```

        :param link: A Bitlink made of the domain and hash
        :param unit: A unit of time ("minute" "hour" "day" "week" "month")
        :param units: An integer representing the time units to query data for. pass -1 to return all units of time.
        :param size: The quantity of items to be be returned (1..1000)
        :param rollup: Should we roll-up results?
        :param unit_reference_ts: An ISO-8601 timestamp, indicating the most recent time for which to pull metrics. Will default to current time.
        """
        endpoint = '/link/clicks'
        # Generate params
        params = {
            'link': link,
            'timezone': 0,
            'unit': unit,
            'units': units,
            'size': size,
            'rollup': 'true' if rollup else 'false'
        }
        if unit_reference_ts:
            params['unit_reference_ts'] = unit_reference_ts
        return self.get(endpoint, params)

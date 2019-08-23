import csv
import datetime
import json
import os
from abc import ABC, abstractmethod
from collections import OrderedDict

import dateutil.parser

from src.util import epoch


class Output(ABC):
    @abstractmethod
    def save(self, filename, progress, clicks, referrers, countries):
        """
        Save the current statistics and progress to the specified file
        :param filename: The file to save to
        :param progress: The current progress in the form of an integer of the current index
        :param clicks: The current number of clicks
        :param referrers: The current referrer values
        :param countries: The current country values
        """
        pass

    @abstractmethod
    def load(self, filename):
        """
        Load the progress, clicks, referrers, and countries from the specified filename
        :param filename:
        :return: Tuple of (progress, clicks, referrers, countries)
        """
        pass


class JsonOutput(Output):
    def save(self, filename, progress, clicks, referrers, countries, finished=False):
        obj = {
            'clicks': clicks,
            'referrers': referrers,
            'countries': countries,
            'progress': progress,
        }

        with open(filename, 'w+') as f:
            json.dump(obj, f)

    def load(self, filename):
        if not os.path.isfile(filename):
            progress = 0
            clicks = {}
            referrers = OrderedDict()
            countries = OrderedDict()
        else:
            with open(filename, 'r+') as f:
                obj = json.load(f)
                progress = obj.get('progress', 0)
                clicks = obj.get('clicks', {})
                referrers = obj.get('referrers', OrderedDict())
                countries = obj.get('countries', OrderedDict())

        return progress, clicks, referrers, countries


class CsvOutput(Output):
    def _gen_rows(self, category, dictionary):
        rows = []
        sortedkeys = list(dictionary.keys())
        sortedkeys.sort()
        for key in sortedkeys:
            rows.append([category, key, dictionary.get(key)])
        return rows

    def _gen_click_rows(self, dictionary):
        rows = []
        sortedkeys = list(dictionary.keys())
        sortedkeys.sort()
        for key in sortedkeys:
            rows.append(['Clicks', datetime.datetime.fromtimestamp(key).isoformat(), dictionary.get(key)])
        return rows

    def save(self, filename, progress, clicks, referrers, countries):
        # A little hacky, store progress in the header
        rows = [['Category', 'Key', 'Clicks', progress]]
        rows += self._gen_click_rows(clicks)
        rows += self._gen_rows('Countries', countries)
        rows += self._gen_rows('Referrers', referrers)
        with open(filename, 'w+', newline='') as f:
            writer = csv.writer(f, lineterminator='\n', escapechar='\\')
            writer.writerows(rows)

    def load(self, filename):
        progress = 0
        clicks = {}
        countries = {}
        referrers = {}
        with open(filename, 'r+', newline='') as f:
            reader = csv.reader(f, lineterminator='\n', escapechar='\\')
            # Pop the first row
            header = next(reader)
            progress = int(header[-1])
            for row in reader:
                category = row[0]
                key = row[1]
                value = int(row[2])
                if category == 'Clicks':
                    date = epoch(dateutil.parser.parse(key))
                    clicks[date] = value
                elif category == 'Countries':
                    countries[key] = value
                elif category == 'Referrers':
                    referrers[key] = value
        return progress, clicks, referrers, countries

import logging
from collections import OrderedDict
from datetime import datetime
from operator import itemgetter


def get_max_val(dictionary: OrderedDict, count=0):
    dictionary = OrderedDict(sorted(dictionary.items(), key=itemgetter(1), reverse=True))
    if count == 0:
        key = [key for key in dictionary][0]
        yield key, dictionary[key]
        return
    cur_count = 0
    for key in dictionary:
        cur_count += 1
        if cur_count > count:
            break
        yield key, dictionary.get(key)


def print_stats(countries, referrers, country_limit, referrer_limit, checkpoint=True):
    if checkpoint:
        max_country, country_clicks = next(get_max_val(countries))
        msg = "Current stats: "
    else:
        msg = "Final Results:"

    msg += "\nTop {} Countries:".format(country_limit)
    for key, value in get_max_val(countries, count=country_limit):
        msg += "\n- {} ({} clicks)".format(key, value)

    msg += "\nTop {} Referring domains:".format(referrer_limit)
    for key, value in get_max_val(referrers, count=referrer_limit):
        msg += "\n- {} ({} clicks)".format(key, value)

    if checkpoint:
        msg += "\n\n"
    logging.info(msg)

def epoch(date):
    return (date - datetime.utcfromtimestamp(0)).total_seconds()
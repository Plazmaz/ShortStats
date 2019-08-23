import json
import os

import click
import logging
from collections import OrderedDict
from operator import itemgetter
from time import sleep

from src.bitly_info import BitlyAPI
from src.outputs import JsonOutput, CsvOutput
from src.util import print_stats

logging.basicConfig(format='%(asctime)s %(message)s')
logging.getLogger().setLevel(logging.INFO)

BANNER = """
                   &&%%###((####%%%@&                      
              @%#(*,,....,/*.      ,(/##&                  
           %/.   .//,,**           ,/,,/##&              
         ##(.         ,(( *@@@@&,     *,...,/(&            
       #(,/            ./ #@@@@@*      *.....,/(&    (#    
  (( *./*     .#@@@(  /  ,(#(.      /*.......,(#%(*.,(   
 &*.*#,..,*     /@@@@@, #/.          /*..........//...,#   
 /*,(,...,*/     ,%&%* /,,*(*..  .,(*,............//.../   
 #,(*......,/*.     ./*,*///////**,................(*..*   
 #*/..........,*///#/,             .*(*,...........,(,*#   
  %*...........,(*   ,#&@@@@@@@@@@,  .(*..........(&#(&
  &*........../*  ,&@@@@@@@@@@@@@@@@@@&, .(,......../,...,#
  &*.........**  #@@@@@@@@@@@@@@@@@@@@@@#  (,......./,....(
   /........./. ,@@@@@@@@@@@@@@@@@@@@@@@@, /*......,(,...,(
   %,........**  &@@@@@@@@@@@@@@@@@@@@@@&  (,......**,...,#
    /........,(. .&@@@@@@@@@@@@@@@@@@@@&. /*......,/,....*,
    @/.........*/  .#@@@@@@@@@@@@@@@@#. ,(,......,(*,...,# 
     @(,.........,//.  .,/#%%%%#/,.  *(*,.......,@    #/(  
       @,............,*/((//////(//*,.........,/@          
         %,.................................,/@            
           @*,............................,#@              
              @/,.....................,*%@                 
                  @@(*,,.......,,*/#@@                     
 ____  _     ____  ____  _____  ____  _____  ____  _____  ____ 
/ ___\/ \ /|/  _ \/  __\/__ __\/ ___\/__ __\/  _ \/__ __\/ ___\\
|    \| |_||| / \||  \/|  / \  |    \  / \  | / \|  / \  |    \\
\___ || | ||| \_/||    /  | |  \___ |  | |  | |-||  | |  \___ |
\____/\_/ \|\____/\_/\_\  \_/  \____/  \_/  \_/ \|  \_/  \____/
                                                               
"""

def set_referrers(link, cur_vals, connection):
    try:
        raw = connection.get_referrers(link)
    except RuntimeError as e:
        logging.exception("Experienced runtime error... Trying again in two seconds.", e)
        sleep(2)
        set_referrers(link, cur_vals, connection)
        return

    referrers = raw.get('data').get('referrers')
    for obj in referrers:
        # Prefer url, but fall back to domain
        # key = obj.get('url', obj.get('domain'))
        key = obj.get('referrer')
        if key in cur_vals:
            cur_vals[key] += obj.get('clicks')
        else:
            cur_vals[key] = obj.get('clicks')


def set_countries(link, cur_vals, connection):
    try:
        raw = connection.get_countries(link)
    except RuntimeError as e:
        logging.exception("Experienced runtime error... Trying again in two seconds.", e)
        sleep(2)
        set_countries(link, cur_vals, connection)
        return

    countries = raw.get('data').get('countries')
    for country in countries:
        key = country.get('country')
        if key in cur_vals:
            cur_vals[key] += country.get('clicks')
        else:
            cur_vals[key] = country.get('clicks')


def get_clicks(link, connection):
    try:
        return connection.get_clicks(link, rollup=False)
    except RuntimeError as e:
        logging.exception("Experienced runtime error... Trying again in two seconds.", e)
        sleep(2)
        return get_clicks(link, connection)


def process_list(links, connection, quiet, country_limit_checkpoint, country_limit, referrer_limit_checkpoint,
                 referrer_limit, storage_backend_cls, out_file, clicks=None, referrers=None, countries=None, offset=0):
    storage = storage_backend_cls()
    links = links[offset:]
    total_links = len(links)
    click_data = clicks or {}
    countries = OrderedDict(countries)
    referrers = OrderedDict(referrers)
    for i in range(0, len(links)):
        # Strip newline
        link = links[i].strip()
        set_referrers(link, referrers, connection)
        set_countries(link, countries, connection)

        cur_data = get_clicks(link, connection).get('data')
        for event in cur_data.get('link_clicks'):
            key = event.get('dt')
            if key in click_data:
                click_data[key] += event.get('clicks')
            else:
                click_data[key] = event.get('clicks')
        # Checkpoint
        if i % 50 == 0 and i != 0:
            storage.save(out_file, i, click_data, referrers, countries)
            pctage = (i / total_links) * 100
            logging.info('Reached checkpoint. Progress: {}/{} ({}%)'.format(i, total_links, pctage))
            if not quiet:
                # Print checkpoint stats
                print_stats(countries, referrers, country_limit_checkpoint, referrer_limit_checkpoint)

    if not quiet:
        print_stats(countries, referrers, country_limit,
                    referrer_limit, checkpoint=False)

    storage.save(out_file, total_links, click_data, referrers, countries)


@click.command()
@click.option('--in-file', default='links.txt', help='The file to pull bitlinks from', type=click.File('r+'), show_default=True)
@click.option('--token', envvar='BITLY_TOKEN', help='Your bitly generic access token (https://bitly.is/accesstoken). Can also be set in BITLY_TOKEN.', type=str, required=True)
@click.option('--quiet', default=False, is_flag=True, help='Skip generating and printing of statistics, only save data', type=bool)
@click.option('--save-format', default='json', help='Specify the output file format.', type=click.Choice(['csv', 'json']), show_default=True)
@click.option('--country-limit-checkpoint', default=10, help='The maximum number of countries to display when reporting progress', type=int, show_default=True)
@click.option('--country-limit', default=30, help='The maximum number of countries to display when progress is complete.', type=int, show_default=True)
@click.option('--referrer-limit-checkpoint', default=10, help='The maximum number of referrers to display when reporting progress', type=int, show_default=True)
@click.option('--referrer-limit', default=30, help='The maximum number of referrers to display when progress is complete.', type=int, show_default=True)
@click.option('--out-file', default='output', help='The output filename (extension will be appended depending on output)', type=click.Path(), show_default=True)
@click.option('--resume-file', help='The save file to load from. If specified, we will attempt to resume a previous session', type=click.Path(exists=True))
@click.option('--start-offset', default=0, help='The offset index to start at', type=int, show_default=True)
def summarize(in_file, token, quiet, save_format, country_limit_checkpoint,
              country_limit, referrer_limit_checkpoint, referrer_limit, out_file, resume_file, start_offset):
    connection = BitlyAPI(token)
    # Unused Regexp for bitlinks: .*https?\://bit\.ly/(.*?)[^\w-].*
    links = in_file.readlines()
    logging.info('Found {} links. Gathering aggregates...'.format(len(links)))
    storage_backend = {
        'json': JsonOutput,
        'csv': CsvOutput
    }[save_format.lower()]

    extension = {
        'json': 'json',
        'csv': 'csv'
    }[save_format.lower()]
    clicks = {}
    referrers = {}
    countries = {}
    progress = 0
    if resume_file:
        progress, clicks, referrers, countries = storage_backend().load(resume_file)
        logging.info("Found resume file. Resetting to idx=%d", progress)

    if progress == 0 and start_offset != 0:
        progress = start_offset
        logging.info("Manual offset override set. Resetting to idx=%d", progress)

    filename = os.path.abspath(out_file + '.' + extension)
    process_list(links, connection, quiet, country_limit_checkpoint, country_limit,
                 referrer_limit_checkpoint, referrer_limit, storage_backend, filename,
                 clicks, referrers, countries, progress)


if __name__ == '__main__':
    print(BANNER)
    summarize()

#! /usr/bin/env python

from __future__ import print_function

from datetime import datetime
import json

MAX_ENTRIES_PER_LINE = 4

rows = [
    'launch',
    'docked',
    'crane_cap_on_booster',
    'ship_lift_start',
    'ship_lift_finish',
    'first_leg_started',
    'last_leg_finished',
    'horizontal',
    'transported',
]

def get_calcs():
    return [
        make_time_calc('launch', 'docked', 'days'),
        make_time_calc('docked', 'ship_lift_start', 'hours'),
        make_time_calc('docked', 'ship_lift_finish', 'hours'),
        make_time_calc('docked', 'first_leg_started', 'days'),
        make_time_calc('docked', 'last_leg_finished', 'days'),
        make_time_calc('docked', 'horizontal', 'days'),
        make_time_calc('docked', 'transported', 'days'),
    ]

def parse_date(dstr):
    return datetime.strptime(dstr, '%Y-%m-%d %H:%M')

def date_diff(entry, end_name, start_name):
    end_time = parse_date(entry['dates_utc'][end_name])
    start_time = parse_date(entry['dates_utc'][start_name])
    return end_time - start_time

def make_time_calc(start, end, units):
    time_conv = {
        'hours': lambda diff: diff.total_seconds() / 60 / 60,
        'days': lambda diff: diff.total_seconds() / 60 / 60 / 24
    }
    name = start + ' to ' + end + ' (' + units + ')'
    def calc(entry):
        if entry['dates_utc'][end] and entry['dates_utc'][start]:
            return time_conv[units](date_diff(entry, end, start))
        return None
    return name, calc

def make_link(text, url):
	safe_text = text.replace(']', '\\]')
	safe_url = url.replace(')', '\\)')
	return '[' + safe_text + ']' + '(' + safe_url + ')'

def make_row(row_name, cols):
    display_row_name = row_name.replace('_', ' ')
    return '| ' + '| '.join([display_row_name] + cols) + '|\n'

def make_table(all_data):
    md = ''
    calcs = get_calcs() # only used for name and order here
    for idx in range(0, len(all_data), MAX_ENTRIES_PER_LINE):
        data = all_data[idx : idx + MAX_ENTRIES_PER_LINE]

        name_links = [make_link(entry['mission_name'], entry['recovery_thread']) for entry in data]
        md += '| | ' + '| '.join(name_links) + '|\n'
        dashes = ['---' for entry in data]
        md += '| ---| ' + '| '.join(dashes) + '|\n'

        md += make_row('notes', [entry['notes'] for entry in data])

        for row_name in rows:
            cols = [entry['dates_utc'][row_name] for entry in data]
            md += make_row(row_name, cols)

        for row_name, fn in calcs:
            cols_data = [entry[row_name] for entry in data]
            cols = ['{:.02f}'.format(x) if x != None else '' for x in cols_data]
            display_row_name = row_name.replace('_', ' ')
            md += '| ' + '| '.join([display_row_name] + cols) + '|\n'
        md += '\n'
    return md

def add_calcs(data):
    calcs = get_calcs()
    for entry in data:
        for row_name, fn in calcs:
            entry[row_name] = fn(entry)
    return data

def add_record_time(data):
    calcs = get_calcs()
    entry = {k:'' for k,v in data[0].items()}
    entry['dates_utc'] = {k:'' for k,v in data[0]['dates_utc'].items()}
    for row_name, fn in calcs:
        entry[row_name] = 99999
    entry['mission_name'] = 'Record Times'
    entry['recovery_thread'] = 'https://www.reddit.com/r/spacex/wiki/recovery_timing'
    entry['notes'] = ''
    for row_name, fn in calcs:
        for d in data:
            v = d[row_name]
            if v != None and v < entry[row_name]:
                entry[row_name] = v
        entry[row_name]
    return [entry] + data

def add_average(data):
    calcs = get_calcs()
    entry = {k:'' for k,v in data[0].items()}
    entry['dates_utc'] = {k:'' for k,v in data[0]['dates_utc'].items()}
    entry['mission_name'] = 'Average'
    entry['recovery_thread'] = 'https://www.reddit.com/r/spacex/wiki/recovery_timing'
    for row_name, fn in calcs:
        row = [d[row_name] for d in data if d[row_name] != None]
        entry[row_name] = sum(row) / len(row)
    return [entry] + data

def process_data(data):
    data = add_calcs(data)
    # data = add_average(data)
    data = add_record_time(data)
    return data

def main():
    with open('data.json', 'rb') as f:

        all_data = json.load(f)

        print('### East Coast Landings\n')
        east_coast_processed = process_data([x for x in all_data if x['port'] == 'Port Canaveral'])
        print(make_table(east_coast_processed))

        print('### West Coast Landings\n')
        west_coast_processed = process_data([x for x in all_data if x['port'] == 'Port of L.A.'])
        print(make_table(west_coast_processed))



if __name__ == '__main__':
    main()

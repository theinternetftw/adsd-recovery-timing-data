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
    'first_leg_piston_removed',
    'last_leg_removed',
    'horizontal',
    'transported',
    'relaunch'
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

calcs = [
    make_time_calc('launch', 'docked', 'days'),
    make_time_calc('docked', 'ship_lift_start', 'hours'),
    make_time_calc('docked', 'ship_lift_finish', 'hours'),
    make_time_calc('docked', 'last_leg_removed', 'days'),
    make_time_calc('docked', 'horizontal', 'days'),
    make_time_calc('docked', 'transported', 'days'),
    make_time_calc('launch', 'relaunch', 'days'),
]

def make_table(all_data):
    md = ''
    for idx in range(0, len(all_data), MAX_ENTRIES_PER_LINE):
        data = all_data[idx : idx + MAX_ENTRIES_PER_LINE]

        names = [entry['mission_name'] for entry in data]
        md += '| | ' + '| '.join(names) + '|\n'
        dashes = ['---' for entry in data]
        md += '| ---| ' + '| '.join(dashes) + '|\n'

        for row_name in rows:
            cols = [entry['dates_utc'][row_name] for entry in data]
            display_row_name = row_name.replace('_', ' ')
            md += '| ' + '| '.join([display_row_name] + cols) + '|\n'

        for row_name, fn in calcs:
            cols_data = [fn(entry) for entry in data]
            cols = ['{:.02f}'.format(x) if x != None else '' for x in cols_data]
            display_row_name = row_name.replace('_', ' ')
            md += '| ' + '| '.join([display_row_name] + cols) + '|\n'
        md += '\n'
    return md

def main():
    with open('data.json', 'rb') as f:

        all_data = json.load(f)

        print('### East Coast Landings:\n')
        print(make_table([x for x in all_data if x['port'] == 'Port Canaveral']))

        print('### West Coast Landings:\n')
        print(make_table([x for x in all_data if x['port'] == 'Port of L.A.']))



if __name__ == '__main__':
    main()

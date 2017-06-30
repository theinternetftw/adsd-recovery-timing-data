#! /usr/bin/env python

from __future__ import print_function

from datetime import datetime
import json

required_structure = {
    'mission_name': str,
    'port': 'port',
    'dates_utc': {
        'launch': 'time',
        'docked': 'time',
        'crane_cap_on_booster': 'time',
        'ship_lift_start': 'time',
        'ship_lift_finish': 'time',
        'first_leg_piston_removed': 'time',
        'last_leg_removed': 'time',
        'horizontal': 'time',
        'transported': 'time',
        'relaunch': 'time',
    }
}

def check_types(ref, test):
    if ref == 'time':
        assert test == '' or datetime.strptime(test, '%Y-%m-%d %H:%M')
    elif ref == 'port':
        assert test in ['Port Canaveral', 'Port of L.A.']
    elif ref == str:
        errmsg = repr(test) + ' doesn\'t match ' + repr(ref)
        assert type(test) == str or type(test) == unicode, errmsg
    else:
        assert False, 'can\'t validate unknown type ref: ' + repr(ref)

def check_keys(ref, test):
    for x in ref:
        assert x in test, x + ' should be a key in ' + repr(test)
    for t in test:
        assert t in ref, repr(t) + ' not an expected key: ' + repr(ref)

def check_dict(ref, d):
    assert type(d) == dict, repr(d) + ' should be dict'
    check_keys(ref, d)
    for key, val in ref.items():
        if type(val) == dict:
            check_dict(ref[key], d[key])
        else:
            check_types(val, d[key])

def main():
    with open('data.json', 'rb') as f:
        data = json.load(f)
        for entry in data:
            check_dict(required_structure, entry)

if __name__ == '__main__':
    main()

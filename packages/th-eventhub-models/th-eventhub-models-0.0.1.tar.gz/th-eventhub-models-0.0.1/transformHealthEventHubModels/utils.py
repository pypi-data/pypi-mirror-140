import json
import re

from dateutil import parser


def date_string(string):
    return re.search("^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}", string)


def decodeUTFString(encoded_string):
    return encoded_string.decode('UTF-8')


def type_corrected_json_load(encoded_string):
    decoded_dict = json.loads(decodeUTFString(encoded_string))
    for (key, value) in decoded_dict.items():
        if isinstance(value, str) and date_string(value):
            decoded_dict[key] = parser.parse(value)
    return decoded_dict

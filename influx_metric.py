import time
from enum import Enum


class _InfluxFieldType(Enum):
    STRING = 0
    INTEGER = 1
    FLOAT = 2


class _InfluxField(object):

    def __init__(self, name: str, value: (str | int | float)):
        # handle commas, equal-sign, and spaces in field names
        self.name = name \
            .replace(',', r'\,') \
            .replace('=', r'\=') \
            .replace(' ', r'\ ')

        self.value = value

        if type(value) == str:
            self.field_type = _InfluxFieldType.STRING
            # handle double-quotes and backslashes in string field values
            self.value = value \
                .replace('\\', '\\\\') \
                .replace(r'"', r'\"')

        elif type(value) == int:
            self.field_type = _InfluxFieldType.INTEGER
        elif type(value) == float:
            self.field_type = _InfluxFieldType.FLOAT
        else:
            raise TypeError(f'unsupported type "{type(value)}" for an influx field')

    def __str__(self):
        if self.field_type == _InfluxFieldType.STRING:
            return f'{self.name}="{self.value}"'

        if self.field_type == _InfluxFieldType.INTEGER:
            return f'{self.name}={self.value}i'

        if self.field_type == _InfluxFieldType.FLOAT:
            return f'{self.name}={self.value}'


class InfluxMetric(object):

    # force at least one field to be populated
    def __init__(self, name: str, timestamp_ns: int | None = None):
        if not name:
            raise ValueError("Metric name is required")

        if name[0] == '_':
            raise ValueError("Influx metrics cannot start with an underscore")

        # escape commas and spaces in metric names
        self.name: str = name \
            .replace(',', r'\,') \
            .replace(' ', r'\ ')

        self.tags: list[dict] = []
        self.fields: list[_InfluxField] = []
        self.timestamp_ns: int = timestamp_ns or 0

    def with_tag(self, name: str, value: str):
        # if only python was typed
        if type(name) != str or type(value) != str:
            raise TypeError("Influx tag names/values must be strings")

        # ensure the name and value are populated
        if name and value:

            if name[0] == '_':
                raise ValueError("Influx tags cannot start with an underscore")

            # handle commas, equal-sign, and spaces in tag names
            name = name \
                .replace(',', r'\,') \
                .replace('=', r'\=') \
                .replace(' ', r'\ ')

            # handle commas, equal-sign, and spaces in tag values
            value = value \
                .replace(',', r'\,') \
                .replace('=', r'\=') \
                .replace(' ', r'\ ')

            self.tags.append({'name': name, 'value': value})
        return self

    def with_field(self, name: str, value: (str | int | float)):
        # ensure the name is populated
        if name:
            if name[0] == '_':
                raise ValueError("Influx fields cannot start with an underscore")
            self.fields.append(_InfluxField(name, value))
        return self

    def with_timestamp(self, timestamp_ns: int):
        self.timestamp_ns = timestamp_ns
        return self

    def __str__(self):
        # ensure we have a timestamp to use, default to now() if there isn't one
        if not self.timestamp_ns:
            self.with_timestamp(time.time_ns())

        if not len(self.fields):
            raise RuntimeError(f"At least one field is required for metric {self.name}")

        influx_line = self.name

        if len(self.tags):
            # sort tags alphabetically by their name
            self.tags.sort(key=lambda x: x["name"])
            # append to the builder
            for tag in self.tags:
                influx_line += f',{tag["name"]}={tag["value"]}'

        # add first whitespace to separate the name (and optional tags) from the fields
        influx_line += ' '

        # sort fields alphabetically by their name
        self.fields.sort(key=lambda x: x.name)
        influx_line += ','.join(str(f) for f in self.fields)

        # add the second whitespace to separate the field(s) and the timestamp, then add the timestamp
        influx_line += f' {self.timestamp_ns}'

        return influx_line

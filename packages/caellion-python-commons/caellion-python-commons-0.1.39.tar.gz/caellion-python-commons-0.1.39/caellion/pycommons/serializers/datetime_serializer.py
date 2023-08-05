"""!
This module provides various serializers for datetime.datetime object
"""

import datetime
import math


class DateTimeIsoTimeSerializer:
    """!
    Implementation of DateTime serializer, using IsoTime as a serialized standard.
    """

    ## Alias for unserialize
    @staticmethod
    def deserialize(serialized_string):
        """!
        Unserializes the ISO string to DateTime object.
        Always returns UTC timezone DateTime.

        Alias for unserialize()

        @param serialized_string serialized datetime to unserialize
        @returns DateTime with UTC timezone
        """
        return __class__.unserialize(serialized_string)

    @staticmethod
    def unserialize(serialized_string):
        """!
        Unserializes the ISO string to DateTime object.
        Always returns UTC timezone DateTime.

        @param serialized_string serialized datetime to unserialize
        @returns DateTime with UTC timezone
        """
        return datetime.datetime.fromisoformat(serialized_string)

    @staticmethod
    def serialize(datetime_to_serialize):
        """!
        Serializes the DateTime to ISO string.
        Always returns UTC timezone string.

        @param datetime_to_serialize DateTime to serialize to UTC timezoned ISO string
        @returns ISO String
        """
        return datetime_to_serialize.astimezone(datetime.timezone.utc).isoformat()


class DateTimeUnixMillisSerializer:
    """!
    Implementation of DateTime serializer, using Unix-epoch based timestamp with millisecond precision as serialized format.
    """

    ## Alias for unserialize
    @staticmethod
    def deserialize(integer):
        """!
        Unserializes the unix timestamp with millisecond precision to DateTime object.
        Always returns UTC timezone DateTime.

        Alias for unserialize()

        @param integer unix timestamp integer (milliseconds)
        @returns DateTime with UTC timezone
        """
        return __class__.unserialize(integer)

    @staticmethod
    def unserialize(integer):
        """!
        Unserializes the unix timestamp with millisecond precision to DateTime object.
        Always returns UTC timezone DateTime.

        @param integer unix timestamp integer (milliseconds)
        @returns DateTime with UTC timezone
        """
        return datetime.datetime.fromtimestamp(integer / 1000.0).astimezone(datetime.timezone.utc)

    @staticmethod
    def serialize(datetime_to_serialize):
        """!
        Serializes the DateTime to Unix timestamp integer with millisecond precision.
        Always returns UTC timezone integer.

        @param datetime_to_serialize DateTime to serialize to unix timestamp integer
        @returns unix timestamp integer (milliseconds)
        """
        epoch = datetime.datetime.fromtimestamp(0).astimezone(datetime.timezone.utc)
        datetime_to_serialize = datetime_to_serialize.astimezone(datetime.timezone.utc)
        ts = (datetime_to_serialize - epoch).total_seconds() * 1000.0
        ts = math.floor(ts)
        return ts


class DateTimeUnixMicrosSerializer:
    """!
    Implementation of DateTime serializer, using Unix-epoch based timestamp with microsecond precision as serialized format.
    """

    ## Alias for unserialize
    @staticmethod
    def deserialize(integer):
        """!
        Unserializes the unix timestamp with microsecond precision to DateTime object.
        Always returns UTC timezone DateTime.

        Alias for unserialize()

        @param integer unix timestamp integer (microseconds)
        @returns DateTime with UTC timezone
        """
        return __class__.unserialize(integer)

    @staticmethod
    def unserialize(integer):
        """!
        Unserializes the unix timestamp with microsecond precision to DateTime object.
        Always returns UTC timezone DateTime.

        @param integer unix timestamp integer (microseconds)
        @returns DateTime with UTC timezone
        """
        return datetime.datetime.fromtimestamp(integer / 1000000.0).astimezone(datetime.timezone.utc)

    @staticmethod
    def serialize(datetime_to_serialize):
        """!
        Serializes the DateTime to Unix timestamp integer.
        Always returns UTC timezone integer.

        @param datetime_to_serialize DateTime to serialize to unix timestamp integer
        @returns unix timestamp integer (microseconds)
        """
        epoch = datetime.datetime.fromtimestamp(0).astimezone(datetime.timezone.utc)
        datetime_to_serialize = datetime_to_serialize.astimezone(datetime.timezone.utc)
        ts = (datetime_to_serialize - epoch).total_seconds() * 1000000.0
        ts = math.floor(ts)
        return ts


class DateTimeUnixSerializer:
    """!
    Implementation of DateTime serializer, using Unix-epoch based timestamp with second precision as serialized format.
    """

    ## Alias for unserialize
    @staticmethod
    def deserialize(integer):
        """!
        Unserializes the unix timestamp with second precision to DateTime object.
        Always returns UTC timezone DateTime.

        Alias for unserialize()

        @param integer unix timestamp integer (seconds)
        @returns DateTime with UTC timezone
        """
        return __class__.unserialize(integer)

    @staticmethod
    def unserialize(integer):
        """!
        Unserializes the unix timestamp with second precision to DateTime object.
        Always returns UTC timezone DateTime.

        @param integer unix timestamp integer (seconds)
        @returns DateTime with UTC timezone
        """
        return datetime.datetime.fromtimestamp(integer / 1.0).astimezone(datetime.timezone.utc)

    @staticmethod
    def serialize(datetime_to_serialize):
        """!
        Serializes the DateTime to Unix timestamp integer with seconds precision.
        Always returns UTC timezone integer.

        @param datetime_to_serialize DateTime to serialize to unix timestamp integer
        @returns unix timestamp integer (seconds)
        """
        epoch = datetime.datetime.fromtimestamp(0).astimezone(datetime.timezone.utc)
        datetime_to_serialize = datetime_to_serialize.astimezone(datetime.timezone.utc)
        ts = (datetime_to_serialize - epoch).total_seconds() * 1.0
        ts = math.floor(ts)
        return ts

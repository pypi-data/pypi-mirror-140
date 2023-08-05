"""!
This module provides various string formatters
"""

import math


class InvalidDurationException(Exception):
    """!
    This exception is raised whenever provided duration is zero or negative.
    """

    pass


class NumberFormatting:
    """!
    This class provides various number formats
    """

    def formatSI(v, dec=0):
        """!
        Formats number as an SI-prefixed decimal

        @param v Number to be formatted
        @param dec Number of decimal places

        @returns formatted string
        """
        sign = ""
        if v < 0:
            sign = "-"
            v = abs(v)
        suffix = ""
        SI_suffix = "kMGTPEZY"

        if v >= 1000:
            value_mag = math.log10(v)

            suffix_index = min(len(SI_suffix) - 1, max(0, math.floor(value_mag / 3) - 1))

            value = v / pow(10, (suffix_index + 1) * 3)
            suffix = SI_suffix[suffix_index]
        else:
            value = v

        return sign + ("{:." + str(dec) + "f}").format(value) + suffix

    def formatBinarySI(v, dec=0):
        """!
        Formats number as an SI-prefixed decimal, using binary unit prefixes (ki, Mi, etc.)

        @param v Number to be formatted
        @param dec Number of decimal places

        @returns formatted string
        """
        sign = ""
        if v < 0:
            sign = "-"
            v = abs(v)
        suffix = ""
        SI_suffix = "kMGTPEZY"

        if v >= 1024:
            value_mag = math.log(v, 2)

            suffix_index = min(len(SI_suffix) - 1, max(0, math.floor(value_mag / 10) - 1))

            value = v / pow(2, (suffix_index + 1) * 10)
            suffix = SI_suffix[suffix_index] + "i"
        else:
            value = v

        return sign + ("{:." + str(dec) + "f}").format(value) + suffix

    # for formatting less than one (0.X) with suffixes like milli
    def formatSISubValue(v, dec=0):
        """!
        Formats less-than-one numbers to an SI-prefixed decimal (using prefixes like m, μ)

        @param v Number to be formatted
        @param dec Number of decimal places

        @returns formatted string
        """
        sign = ""
        if v < 0:
            sign = "-"
            v = abs(v)
        SI_suffix = "mμnpfazy"
        max_log = (len(SI_suffix)) * 3

        if v >= 1 / pow(10, max_log):
            value_mag = -1 * math.log10(v)
            suffix_index = math.ceil(value_mag / 3) - 1
            value = v * pow(10, (suffix_index + 1) * 3)
            suffix = SI_suffix[suffix_index]
        elif v > 0:
            value = 0
            suffix = "y"
        else:
            value = 0
            suffix = ""

        return sign + ("{:." + str(dec) + "f}").format(value) + suffix

    # for formatting less than one (0.X) with suffixes like milli, binary
    def formatSIBinarySubValue(v, dec=0):  # pragma: no mutate
        """!
        Formats fractional number to SI-prefixed decimal using binary unit prefixes

        @warning This is not supported
        """
        return "BinSubValueError"

    # router for formatting all values
    def formatSIFullRange(v, dec):
        """!
        Formats number using full range (will format numbers below 1 with subvalue variant) using SI decimal unit prefixes

        @param v Number to be formatted
        @param dec Number of decimal places

        @returns formatted string
        """
        if v > -1 and v < 1:
            return NumberFormatting.formatSISubValue(v, dec)
        else:
            return NumberFormatting.formatSI(v, dec)

    def formatUnitsPerIntervalDynamic(units, seconds, unit):
        """!
        Generates an expression like "1.0kg/year"

        @param units amount of units that have happened over measurement interval
        @param seconds measurement interval, expressed in seconds
        @param unit name of unit (kg in example above)

        @returns formatted string, expression like "1.0kg/year"
        """
        if units < 0:
            return "-" + NumberFormatting.formatUnitsPerIntervalDynamic(abs(units), seconds, unit)

        if seconds <= 0:
            raise InvalidDurationException(str("{:s} is not a valid, positive duration").format(str(seconds)))

        units_per_second = units / seconds
        units_per_millisecond = units_per_second / 1000.0
        units_per_microsecond = units_per_second / 1000000.0
        units_per_millenium = units_per_second * 1000.0 * 365.0 * 86400.0
        units_per_century = units_per_second * 100.0 * 365.0 * 86400.0
        units_per_year = units_per_second * 365.0 * 86400.0
        units_per_week = units_per_second * 7.0 * 86400.0
        units_per_day = units_per_second * 86400.0
        units_per_hour = units_per_second * 3600.0
        units_per_minute = units_per_second * 60.0

        if units_per_century < 1.0:
            return str("{:.2f}{:s}/{:s}").format(units_per_millenium, unit, "millenium")
        elif units_per_year < 1.0:
            return str("{:.2f}{:s}/{:s}").format(units_per_century, unit, "century")
        elif units_per_week < 1.0:
            return str("{:.2f}{:s}/{:s}").format(units_per_year, unit, "year")
        elif units_per_day < 1.0:
            return str("{:.2f}{:s}/{:s}").format(units_per_week, unit, "week")
        elif units_per_hour < 1.0:
            return str("{:.2f}{:s}/{:s}").format(units_per_day, unit, "day")
        elif units_per_minute < 1.0:
            return str("{:.2f}{:s}/{:s}").format(units_per_hour, unit, "hour")
        elif units_per_second < 1.0:
            return str("{:.2f}{:s}/{:s}").format(units_per_minute, unit, "minute")
        elif units_per_millisecond < 1.0:
            return str("{:.2f}{:s}/{:s}").format(units_per_second, unit, "second")
        elif units_per_microsecond < 1.0:
            return str("{:.2f}{:s}/{:s}").format(units_per_millisecond, unit, "millisecond")
        else:
            return str("{:.2f}{:s}/{:s}").format(units_per_microsecond, unit, "microsecond")

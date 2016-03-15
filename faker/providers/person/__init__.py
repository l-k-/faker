# coding=utf-8

from datetime import timedelta


from .. import BaseProvider
from faker.utils.datetime_safe import date, datetime
from faker.generator import random


localized = True


class Provider(BaseProvider):
    formats = ['{{first_name}} {{last_name}}', ]

    first_names = ['John', 'Jane']

    last_names = ['Doe', ]

    def name(self):
        """
        :example 'John Doe'
        """
        pattern = self.random_element(self.formats)
        return self.generator.parse(pattern)

    def first_name(self, gender=None):
        if gender:
            if gender == "F":
                return self.first_name_female()
            else:
                return self.first_name_male()

        return self.random_element(self.first_names)

    @classmethod
    def last_name(cls):
        return cls.random_element(cls.last_names)

    @classmethod
    def gender(cls):
        return cls.random_element(["F", "M"])

    def name_male(self):
        if hasattr(self, 'formats_male'):
            formats = self.formats_male
        else:
            formats = self.formats
        pattern = self.random_element(formats)
        return self.generator.parse(pattern)

    def name_female(self):
        if hasattr(self, 'formats_female'):
            formats = self.formats_female
        else:
            formats = self.formats
        pattern = self.random_element(formats)
        return self.generator.parse(pattern)

    @classmethod
    def first_name_male(cls):
        if hasattr(cls, 'first_names_male'):
            return cls.random_element(cls.first_names_male)
        return cls.first_name()

    @classmethod
    def first_name_female(cls):
        if hasattr(cls, 'first_names_female'):
            return cls.random_element(cls.first_names_female)
        return cls.first_name()

    @classmethod
    def last_name_male(cls):
        if hasattr(cls, 'last_names_male'):
            return cls.random_element(cls.last_names_male)
        return cls.last_name()

    @classmethod
    def last_name_female(cls):
        if hasattr(cls, 'last_names_female'):
            return cls.random_element(cls.last_names_female)
        return cls.last_name()


    @classmethod
    def prefix(cls):
        if hasattr(cls, 'prefixes'):
            return cls.random_element(cls.prefixes)
        if hasattr(cls, 'prefixes_male') and hasattr(cls, 'prefixes_female'):
            prefixes = cls.random_element((cls.prefixes_male, cls.prefixes_female))
            return cls.random_element(prefixes)
        return ''

    @classmethod
    def prefix_male(cls):
        if hasattr(cls, 'prefixes_male'):
            return cls.random_element(cls.prefixes_male)
        return cls.prefix()

    @classmethod
    def prefix_female(cls):
        if hasattr(cls, 'prefixes_female'):
            return cls.random_element(cls.prefixes_female)
        return cls.prefix()

    @classmethod
    def suffix(cls):
        if hasattr(cls, 'suffixes'):
            return cls.random_element(cls.suffixes)
        if hasattr(cls, 'suffixes_male') and hasattr(cls, 'suffixes_female'):
            suffixes = cls.random_element((cls.suffixes_male, cls.suffixes_female))
            return cls.random_element(suffixes)
        return ''

    @classmethod
    def suffix_male(cls):
        if hasattr(cls, 'suffixes_male'):
            return cls.random_element(cls.suffixes_male)
        return cls.suffix()

    @classmethod
    def suffix_female(cls):
        if hasattr(cls, 'suffixes_female'):
            return cls.random_element(cls.suffixes_female)
        return cls.suffix()

    def birthdate(self, age=None):
        if age is None:
            try:
                age = self.generator.age()
            except:
                # if teh age generator isn't defined for this locale,
                # get a date string between January 1, 1970 and now
                return self.generator.date()

        today = date.today()

        # The oldest (in days) person of age X is the person whose birthday
        # is today (i.e. they officially turn X+1 years old when the date
        # rolls to tomorrow).
        # But if today is Feb 29th and (current year - X) wasn't a leap year,
        # then the oldest person for that age has a March 1st birthday.

        if today.month == 2 and today.day == 29:
            try:
                earliest_bdate = today.replace(year=today.year - age - 1)
            except ValueError:
                earliest_bdate = today.replace(year=today.year - age - 1,
                                               month=3,
                                               day=1)
        else:
            earliest_bdate = today.replace(year=today.year - age - 1)

        # The youngest (in days) person of age X is the person whose birthday
        # was yesterday (i.e. today is the first day they are officially
        # X years old).
        # But if yesterday was Feb 29th and (current year - X - 1) wasn't
        # a leap year, then the youngest person for that age has a Feb 28
        # birthday.

        yesterday = today - timedelta(days=1)
        if yesterday.month == 2 and yesterday.day == 29:
            try:
                latest_bdate = yesterday.replace(year=yesterday.year - age)
            except ValueError:
                latest_bdate = yesterday.replace(year=yesterday.year - age,
                                                 day=28)
        else:
            latest_bdate = yesterday.replace(year=yesterday.year - age)

        # number of potential birthdays for the given age will be 364 or 365,
        # depending on whether the date range includes a Feb 29th
        max_delta = latest_bdate - earliest_bdate

        # now pick a random date within the acceptable range
        delta = timedelta(days=random.randint(0, max_delta.days))

        return (earliest_bdate + delta).strftime('%Y-%m-%d')

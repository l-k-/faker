# coding=utf-8

import csv

from ..en import Provider as PersonProvider
from faker.utils.distribution import choice_distribution
from faker.generator import random


class Provider(PersonProvider):
    # US age distribution is taken from
    # https://www.census.gov/population/age/data/files/2012/2012gender_table1.csv
    # except there the end of the range is >=85 y.o., with the 1.6% probability,
    # which doesn't give a good idea of how fast the tail end is dropping off.
    #
    # https://www.census.gov/prod/cen2010/briefs/c2010br-09.pdf
    # suggests that the 95-99 group consistently (over the 2000-2010 decade)
    # has been clocking in at 0.1%, and the >=100 group doesn't even register.
    #
    # Thus used p(85 to 94) = 1.5 and p(95 to 99) = 0.1

    age_ranges_US = [(0, 4), (5, 9), (10, 14), (15, 19), (20, 24),
                     (25, 29), (30, 34), (35, 39), (40, 44), (45, 49),
                     (50, 54), (55, 59), (60, 64), (65, 69), (70, 74),
                     (75, 79), (80, 84), (85, 94), (95, 99)]

    age_freq_US = [6.5, 6.6, 6.7, 6.9, 7.1, 6.8, 6.6, 6.2, 6.7, 7.0,
                   7.2, 6.6, 5.7, 4.4, 3.2, 2.4, 1.9, 1.5, 0.1]

    last_names_US = []
    last_name_freq_US = []

    with open('faker/providers/person/en_US/1990_census_surnames.csv', mode='r') as f:
        reader = csv.reader(f)

        for row in reader:
            last_names_US.append(row[0].title())
            last_name_freq_US.append(float(row[1]))

    first_names_female_US = []
    first_names_female_freq_US = []

    with open('faker/providers/person/en_US/1990_census_first_female.csv', mode='r') as f:
        reader = csv.reader(f)

        for row in reader:
            first_names_female_US.append(row[0].title())
            first_names_female_freq_US.append(float(row[1]))

    first_names_male_US = []
    first_names_male_freq_US = []

    with open('faker/providers/person/en_US/1990_census_first_male.csv', mode='r') as f:
        reader = csv.reader(f)

        for row in reader:
            first_names_male_US.append(row[0].title())
            first_names_male_freq_US.append(float(row[1]))

    @classmethod
    def age(cls, minor=False):
        if minor:
            # kids' ages are pretty evenly distributed..
            return cls.random_int(0, 20)

        random_range = choice_distribution(cls.age_ranges_US, cls.age_freq_US)
        return random.randint(*random_range)

    @classmethod
    def last_name(cls):
        return choice_distribution(cls.last_names_US, cls.last_name_freq_US)

    @classmethod
    def first_name_female(cls):
        return choice_distribution(cls.first_names_female_US, cls.first_names_female_freq_US)

    @classmethod
    def first_name_male(cls):
        return choice_distribution(cls.first_names_male_US, cls.first_names_male_freq_US)

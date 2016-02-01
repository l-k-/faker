# coding=utf-8

from __future__ import unicode_literals

from faker.generator import random
import faker.utils.stats as stats

from .. import BaseProvider

MRN_DIGITS = 7


class Provider(BaseProvider):
    @classmethod
    def mrn(cls, prefix=''):
        res = str(random.randint(0, pow(10, MRN_DIGITS) - 1))

        # if the number has fewer digits than needed, add leading zeros
        zeros = MRN_DIGITS - len(res)
        return prefix + '0' * zeros + res

    @classmethod
    def mrn_unique(cls, n=2, prefix=''):
        return [(prefix + s) for s in BaseProvider.random_digits_unique(digits=MRN_DIGITS, n=n)]

    def icd9(self, current_age=0,  age=0, gender=None):
        return self.generator.random_digits(3) + '.' + str(self.generator.random_int(min=0, max=200))

    def icd9_unique(self, current_age=0, gender=None, n=2):
        class icd9_iterator():
            def __init__(self):
                self.i = 0
                self.j = 0
                self.n1 = 1000
                self.n2 = 200

            def __iter__(self):
                return self

            def __next__(self):
                if self.i < self.n1:
                    if self.j < self.n2:
                        res = str(self.i).zfill(3) + '.' + str(self.j)
                        self.j += 1
                        return res
                    else:
                        self.j = 0
                        self.i += 1
                        if self.i == self.n1:
                            raise StopIteration()

                        return str(self.i).zfill(3) + '.' + str(self.j)
                else:
                    raise StopIteration()

        return stats.reservoir_sampling(icd9_iterator(), n)

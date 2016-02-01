# coding=utf-8

from __future__ import unicode_literals

import functools
import re
import random

from faker.providers import BaseProvider
import faker.utils.stats as stats

_re_token = re.compile(r'\{\{(\s?)(\w+)(\s?)\}\}')
random = random.Random()


class Generator(object):

    __config = {}

    def __init__(self, **config):
        self.providers = []
        self.__config = dict(
            list(self.__config.items()) + list(config.items()))
        self._num = 1

    @property
    def num(self):
        return self._num

    @num.setter
    def num(self, num):
        self._num = num

    def add_provider(self, provider):

        if type(provider) is type:
            provider = provider(self)

        self.providers.insert(0, provider)

        for method_name in dir(provider):
            # skip 'private' method
            if method_name.startswith('_'):
                continue

            faker_function = getattr(provider, method_name)

            if hasattr(faker_function, '__call__') or \
                    isinstance(faker_function, (classmethod, staticmethod)):
                # add all faker method to generator
                self.set_formatter(method_name, faker_function)

    def provider(self, name):
        try:
            lst = [p for p in self.get_providers()
                   if p.__provider__ == name.lower()]
            return lst[0]
        except IndexError:
            return None

    def get_providers(self):
        """Returns added providers."""
        return self.providers

    @property
    def random(self):
        return random

    def seed(self, seed=None):
        """Calls random.seed"""
        random.seed(seed)

    def format(self, formatter, *args, **kwargs):
        """
        This is a secure way to make a fake from another Provider.
        """
        # TODO: data export?
        return self.get_formatter(formatter)(*args, **kwargs)

    def get_formatter(self, formatter, num=1, sparsity=0, unique=False, options={}, multiple=False):
        """
        Generate num values, where each value can itself be an array of values.

        num: the number of values to generate.
        multiple: - If defined as a dictionary, this argument signifies that each generated value should be
                    an array of values. The fields of the dictionary define the shape of the array.
                  - Otherwise this argument should be set to False, signifying that each generated value
                    is expected to actually be just a single value (i.e. not an array). This is the default.
        """

        # if each value is just a single value (i.e. not an array)
        if not multiple:
            return self._get_formatter_no_multiples(formatter=formatter, num=num, sparsity=sparsity,
                                                    unique=unique, options=options)

        # if we got here, each value is an array of values

        normal_var = stats.RandomNormalVar(min=multiple['min'],
                                           max=multiple['max'],
                                           variance=multiple['variance'],
                                           mean=multiple['mean'])

        # only one value is requested (and this value is an array of values)
        if num < 2:
            return self._get_formatter_no_multiples(formatter=formatter,
                                                    num=normal_var.get_int(),
                                                    sparsity=0,
                                                    unique=(not multiple['duplicates']),
                                                    options=options)

        # num>1 values requested, and each of them is itself an array of values
        def n_values(**args):
            res = []
            if len(args):
                for i in range(num):
                    if sparsity and random.randint(1, 100) <= sparsity:
                        res.append(None)
                    else:
                        arg_set = {}

                        for key in args:
                            arg_set[key] = args[key][i]

                        res.append(self._get_formatter_no_multiples(formatter=formatter,
                                                                    sparsity=0,
                                                                    unique=(not multiple['duplicates']),
                                                                    options=options,
                                                                    num=normal_var.get_int())(**arg_set))
            else:
                for _ in range(num):
                    if sparsity and random.randint(1, 100) <= sparsity:
                        res.append(None)
                    else:
                        res.append(self._get_formatter_no_multiples(formatter=formatter,
                                                                    sparsity=0,
                                                                    unique=(not multiple['duplicates']),
                                                                    options=options,
                                                                    num=normal_var.get_int())())
            return res

        return n_values

    def _get_formatter_no_multiples(self, formatter, num=1, sparsity=0, unique=False, options={}):
        """
        Generate num values, where each value is actually a single value, not an array.
        """
        if num < 2:
            try:
                return functools.partial(getattr(self, formatter), **options)
            except AttributeError:
                raise AttributeError('Unknown formatter "{0}"'.format(formatter))

        if unique:
            try:
                unique_getter = functools.partial(getattr(self, formatter + "_unique"), n=num, **options)
            except AttributeError:
                raise AttributeError('No formatter for unique "{0}"'.format(formatter))

            if sparsity == 0:
                return unique_getter

            def sparserator(**args):
                values = unique_getter(**args)

                for i in range(len(values)):
                    if random.randint(1, 100) <= sparsity:
                        values[i] = None

                return values

            return sparserator

        def n_values_wrapper(**wrapper_args):
            try:
                # if the formatter takes the n argument, then it knows how to generate n values
                # (presumably it's a more efficient method than generating values one by one)
                combined_args = wrapper_args.copy()
                combined_args.update(options)
                return getattr(self, formatter)(n=num, **combined_args)
            except:
                # otherwise we generate the n values one at a time
                try:
                    single_value_provider = functools.partial(getattr(self, formatter), **options)
                except AttributeError:
                    raise AttributeError('Unknown formatter "{0}"'.format(formatter))

                def n_values(**args):
                    res = []
                    if len(args):
                        if sparsity and random.randint(1, 100) <= sparsity:
                            res.append(None)
                        else:
                            for i in range(num):
                                arg_set = {}

                                for key in args:
                                    if isinstance(args[key], list):
                                        arg_set[key] = args[key][i]
                                    else:
                                        # if a list of arguments wasn't given, then each value is generated using the same arguments
                                        arg_set[key] = args[key]

                                res.append(single_value_provider(**arg_set))
                        return res
                    for _ in range(num):
                        if sparsity and random.randint(1, 100) <= sparsity:
                            res.append(None)
                        else:
                            res.append(single_value_provider())
                    return res

                return n_values(**wrapper_args)

        return n_values_wrapper

    def set_formatter(self, name, method):
        """
        This method adds a provider method to generator.
        Override this method to add some decoration or logging stuff.
        """
        setattr(self, name, method)

    def parse(self, text):
        """
        Replaces tokens (like '{{ tokenName }}' or '{{tokenName}}')
        with the result from the token method call.
        """
        return _re_token.sub(self.__format_token, text)

    def __format_token(self, matches):
        formatter = list(matches.groups())
        formatter[1] = self.format(formatter[1])
        return ''.join(formatter)

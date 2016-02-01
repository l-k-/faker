# coding=utf-8

from .. import BaseProvider
from faker import dag

import itertools
import multiprocessing


class Provider(BaseProvider):
    """
    This provider is a collection of functions to generate personal profiles and identities.

    """

    def simple_profile(self):
        """
        Generates a basic profile with personal informations
        """

        sex = self.random_element(["F", "M"])
        if sex == 'F':
            name = self.generator.name_female()
        elif sex == 'M':
            name = self.generator.name_male()
        return {
            "username": self.generator.user_name(),
            "name": name,
            "sex": sex,
            "address": self.generator.address(),
            "mail": self.generator.free_email(),

            #"password":self.generator.password()
            "birthdate": self.generator.date(),

        }

    def profile(self, fields=None, definition=None, num=1):
        if not definition:
            return self.default_profile(fields=fields)
        else:
            return self.spec_profile(definition=definition, num=num)

    def default_profile(self, fields=None):
        """
        Generates a complete profile.
        If "fields" is not empty, only the fields in the list will be returned
        """
        if fields is None:
            fields = []

        d = {
            "job": self.generator.job(),
            "company": self.generator.company(),
            "ssn": self.generator.ssn(),
            "residence": self.generator.address(),
            "current_location": (self.generator.latitude(), self.generator.longitude()),
            "blood_group": "".join(self.random_element(list(itertools.product(["A", "B", "AB", "0"], ["+", "-"])))),
            "website": [self.generator.url() for i in range(1, self.random_int(2, 5))]
        }

        d = dict(d, **self.generator.simple_profile())
        #field selection
        if len(fields) > 0:
            d = dict((k, v) for (k, v) in d.items() if k in fields)

        return d

    def spec_profile(self, definition, num=1):
        """
        Generate a given number of profiles based on the profile definition
        """
        generators = {}
        events = {}

        mgr = multiprocessing.Manager()
        results = mgr.dict()

        self._get_generators(definition, num, generators, events, results)

        for id in generators:
            if '.' in id:
                parts = id.split('.')
                d = definition[parts[0]]['fields']
                for i in range(1, len(parts) - 1):
                    d = d[parts[i]]['fields']
                d = d[parts[-1]]
            else:
                d = definition[id]
            if len(d['context']):
                context = d['context'][0]
                for parameter in context:
                    dependency = context[parameter]
                    generators[id].add_parent(parameter, dependency, events[dependency])
                    generators[dependency].add_child(id)

        # verify that there are no cycles in the dependency graph
        dag.validate(generators)

        for i in generators:
            generators[i].start()
        for i in generators:
            generators[i].join()

        if num == 1:
            return self._reshape_nested_results(results)

        # reformat the results from one giant dictionary to a list
        # of dictionaries, one per generated profile
        res = []
        for i in range(num):
            res.append({})
            for key in results.keys():
                res[i][key] = results[key][i]

        for i in range(num):
            res[i] = self._reshape_nested_results(res[i])

        return res

    @staticmethod
    def _reshape_nested_results(results):
        res = {}
        for key in results.keys():
            if '.' in key:
                r = res
                parts = key.split('.')
                for part in parts[:-1]:
                    r = r.setdefault(part, {})
                r[parts[-1]] = results[key]
            else:
                res[key] = results[key]
        return res

    def _get_generators(self, definition, num, generators, events, results, prefix=None):
        for key in definition:
            prefixed_key = prefix + '.' + key if prefix else key

            self._validate_field(key, definition[key])

            if 'fields' in definition[key]:
                self._get_generators(definition[key]['fields'], num, generators, events, results, prefix=prefixed_key)
                continue

            if 'constant' in definition[key]:
                formatter = self.generator.get_formatter(formatter='constant',
                                                         num=num,
                                                         sparsity=definition[key]['sparsity'],
                                                         unique=False,
                                                         options={'value': definition[key]['constant']},
                                                         multiple=False)
            else:
                formatter = self.generator.get_formatter(formatter=definition[key]['type'],
                                                         num=num,
                                                         sparsity=definition[key]['sparsity'],
                                                         unique=definition[key]['unique'],
                                                         options=definition[key]['options'],
                                                         multiple=definition[key]['multiple'])

            events[prefixed_key] = multiprocessing.Event()
            generators[prefixed_key] = dag.ProcessNode(prefixed_key, formatter, events[prefixed_key], results)

    @classmethod
    def choice(cls, choices):
        return cls.random_element(choices)

    @staticmethod
    def constant(value):
        return value

    @staticmethod
    def _validate_field(name, field):
        if 'choices' in field:
            field['type'] = 'choice'
            field.setdefault('options', {})
            field['options']['choices'] = field['choices']

        if 'context' not in field:
            field['context'] = []
        else:
            if not isinstance(field['context'], list):
                field['context'] = [field['context']]

        if ('multiple' not in field):
            field['multiple'] = False

        if ('options' not in field) or (field['options'] == None):
            field['options'] = {}

        if 'sparsity' in field:
            if (field['sparsity'] < 0 or field['sparsity'] > 100):
                raise ValueError('Value of ' + name + '.sparsity must be a number between 0 and 100')
        else:
            field['sparsity'] = 0

        if ('type' not in field and
                'fields' not in field):
            raise SyntaxError('Type not defined for field ' + field)

        if 'unique' in field:
            field['unique'] = bool(field['unique'])
        else:
            field['unique'] = False

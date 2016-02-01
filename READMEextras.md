## Profile Specification

Faker allows generating complex data profiles based on a YAML specification, without writing any Python code.
For instance, given generators for `name` and `address`, the following specification can be used to generate name-address pairs without having to write a custom name-address profile module in Python:

    name:
        type: name

    address:
        type: address

If this specification is saved in `definition.yml` file, a random name-address pair can then be generated from the command line using

    faker -d=./definition.yml 

resulting in the following output:

    {   
        'name': "Dr. Marjory O'Reilly",
        'address': '28609 Hoppe Plains\nWest Jaydinville, HI 36734'
    }

### Generating multiple profiles

Given a profile specification `definition.yml`, a list of several such profiles can be generated from the command line using the -r (or --repeat) argument. For instance,

    faker -d=./definition.yml -r=3

will produce a list of 3 records:

    [{
        'name': 'Ms. Lynne Spinka PhD',
        'address': 'PSC 6864, Box 3095\nAPO AE 44386'
     },
     {
        'name': 'Ms. Hazel Daniel MD',
        'address': '408 Lexi Villages\nEast Neilview, IN 25877-1769'
     },
     {
        'name': 'Levon Turner',
        'address': '070 Jacobs Falls Suite 426\nAndrashire, NE 46261-0080'
     }]

### Passing arguments to a generator function

If a generator function takes one or more arguments, the values can be passed to it using the `options` field. For instance, if the MRN generator takes a `prefix` argument, the prefix value can be passed in as follows:

    first_name:
        type: first_name

    last_name:
        type: last_name

    mrn:
        type: mrn

        options:
            prefix: MRN_

and the generated records will look something like this:

    [{
        'first_name': 'Dorthea',
        'mrn': 'MRN_2035269',
        'last_name': 'Wyman'
     },
     {
        'first_name': 'Stanton',
        'mrn': 'MRN_0306274',
        'last_name': 'Schamberger'
     }]

### Dependencies

Faker allows specifying dependencies between elements of a profile. For instance, when generating name-gender pairs, we may want to ensure that a gender-appropriate first name is generated. To do this, we use the `context` field:

    first_name:
        type: first_name
        context: 
            gen: gender

    gender:
        type: gender

In this example, the context key `gen` corresponds to the formal argument of the `first_name` generator, and the value `gender` corresponds to the name of the field whose value will be passed in to the generator.

Given this specification and a `first_name` generator that accepts a gender value as its input parameter, Faker will make sure that the gender value is generated first, and that this value is then passed to the first_name generator. 

The list of records generated based on this definition may look like this:
    
    faker -d=./definition.yml -r=4

    [{
        'gender': 'M',
        'first_name': 'Arnold'
     },
     {
        'gender': 'M',
        'first_name': 'Adrian'
     },
     {
        'gender': 'F',
        'first_name': 'Cleva'
     },
     {  
        'gender': 'F',
        'first_name': 'Yvonne'
     }]

Note that there must not be any cycles in dependency specification. 
For instance, trying to generate mock data based on the following specification will result in an error because there is a cyclical dependency between the three elements of the profile:

    first_name:
        type: first_name
        context: 
            gender: gender

    gender:
        type: gender
        context: 
            current_address: address

    address:
        type: address
        context: 
            first_name: first_name

    faker -d=./definition.yml -r=4
    SyntaxError: Loop(s) detected on the following nodes: address, gender, first_name

### Nested profiles

Faker allows nested profile specification. For instance, if we don't have an address generator but only have separate generators for state, city, and zip code, we can still generate name-address pairs using the following nested specification:

    first_name:
        type: first_name

    last_name:
        type: last_name

    address:
        fields:

            state:
                type: state_abbr

            zipcode:
                type: zipcode
                context:
                    state: address.state

            city:
                type: city

Note here that the zip code generator will receive the `state` value as an argument, and it will be able to generate a zip code that actually does exist in the given state. For example,

    faker -d=./definition.yml -r=2

may produce something like this:

    [{
        'first_name': 'Verlie',
        'last_name': 'Schamberger',
        'address': {
            'zipcode': '00654',
            'state': 'PR',
            'city': 'East Estesville'
        }
     },
     {
        'first_name': 'Leonel',
        'last_name': 'Glover',
        'address': {
            'zipcode': '99665',
            'state': 'AK', 
            'city': 'West Izolabury'
        }
     }]

### Multiple values for a field

It is possible to specify a field that accepts an array of values.

For instance, the profile specification below will allow us to generate patient profiles with multiple unique diagnoses each. The number of diagnoses will be a normally distributed random variable within a given range and with a given variance and mean.

    first_name:
        type: first_name

    last_name:
        type: last_name

    diagnoses:
        type: icd9

        multiple:
            duplicates: false
            min: 0
            max: 20
            variance: 5
            mean: 10

Example output:

    faker -d=./definition.yml -r=2

    [{
        'last_name': 'Greenfelder',
        'diagnoses': ['608.164', '702.124', '266.69', '757.46', '174.49', '337.172', '734.114', '243.153', '186.166', '140.57'],
        'first_name': 'Georgette'
     }, 
     {
        'last_name': 'Goyette',
        'diagnoses': ['907.51', '329.194', '704.20', '569.20', '877.124', '922.80', '193.57', '667.152', '195.110'],
        'first_name': 'Alondra'
     }]

### Optimization of multi-record generation

When generating multiple records from the same specification, Faker will attempt to parallelize the generation process. The entire list of values for a given field (e.g. all last names) will be generated sequentially as a unit, but several such lists may be generated in parallel.

For instance, given the specification below, the list of all last names can be generated in parallel with the generation of the list of genders; however, the generation of the list of first names will need to wait till all the gender values have been generated.

    first_name:
        type: first_name
        context: 
            gender: gender

    last_name:
        type: last_name

    gender:
        type: gender

The fact that all values for a given field are generated together as a unit allows to impose the uniqueness constraint on a field, ensuring that no two profiles end up with the same value. For example, the following patient profile specification will allow us to generate patient records with unique MRNs:

    first_name:
        type: first_name

    last_name:
        type: last_name

    mrn:
        type: mrn

        options:
            prefix: MRN_

        unique: true

Example output:

    [{
        'mrn': 'MRN_2602287',
        'last_name': 'Powlowski',
        'first_name': 'Alexandra'
     },
     {
        'mrn': 'MRN_4930665',
        'last_name': 'Boyer',
        'first_name': 'Katharyn'
     },
     {
        'mrn': 'MRN_0057757',
        'last_name': 'Rau',
        'first_name': 'Casey'
     },
     {
        'mrn': 'MRN_9176691',
        'last_name': 'Botsford',
        'first_name': 'Nyasia'
     }]

In addition, since all values for a given field are generated together, the generator for this field may rely on this to introduce its own optimizations to allow generating all N values faster than it would have been to generate these values one by one.



#fom https://stackoverflow.com/a/6792898
def all_uppercase_lowercase_permutations(input_string):
    if not input_string:
        yield ""
    else:
        first = input_string[:1]
        if first.lower() == first.upper():
            for sub_casing in all_uppercase_lowercase_permutations(input_string[1:]):
                yield first + sub_casing
        else:
            for sub_casing in all_uppercase_lowercase_permutations(input_string[1:]):
                yield first.lower() + sub_casing
                yield first.upper() + sub_casing
from flagship import types_validator


def test_decorator_type_value():

    @types_validator(True, {'types': int, 'max_length': 2, 'min_value': 0, 'max_value': 2})
    def test(value):
        pass

    try:
        test(1)
        assert True
    except Exception as e:
        assert False

    try:
        test(4)
        assert False
    except Exception as e:
        assert True

    try:
        test(-3)
        assert False
    except Exception as e:
        assert True

    try:
        test('zlekfnelrkjnlfn')
        assert False
    except Exception as e:
        assert True

def test_decorator_type_dict_value():

    @types_validator(True, {'types': int, 'max_length': 2, 'min_value': 0, 'max_value': 2}, {'types': int, 'max_length': 2, 'min_value': 0, 'max_value': 2})
    def test(value1, value2):
        pass

    try:
        test(1, 1)
        assert True
    except Exception as e:
        assert False

    try:
        test(4, 4)
        assert False
    except Exception as e:
        assert True

    try:
        test(-3, -2)
        assert False
    except Exception as e:
        assert True

    try:
        test('zlekfnelrkjnlfn', 'a')
        assert False
    except Exception as e:
        assert True


def test_decorator_type_dict_value2():

    @types_validator(True, {'types': [int, str], 'max_length': 2, 'min_value': 0, 'max_value': 2})
    def test(value1):
        pass

    try:
        test(1)
        test("aa")
        assert True
    except Exception as e:
        assert False

    try:
        test(1.33)
        assert False
    except Exception as e:
        assert True



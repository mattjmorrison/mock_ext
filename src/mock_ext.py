import mock

def patch_except(klass, *args, **kwargs):
    """
    USAGE:

    @patch_except(SomeClass, some_attribute)
    def test_something(self):
        SomeClass.some_attribute # <= is NOT a mock
        SomeClass.anything_else # <= IS a mock!


    @patch_except(SomeClass, some_attribute, some_other_attribute, ...)
    def test_something(self):
        SomeClass.some_attribute # <= is NOT a mock
        SomeClass.some_other_attribute # <= is NOT a mock
        SomeClass.... # <= is NOT a mock
        SomeClass.something_not_passed_to_patch_except # <= IS a mock!

    @patch_except(SomeClass, some_attribute, with_mock=MagicMock)
    def test_something(self):
        SomeClass.some_attribute # <= is NOT a mock
        SomeClass.something_not_passed_to_patch_except # <= IS a MagicMock!
    """

    mock_class = kwargs.get('with_mock', mock.Mock)

    def first_wrap(func):
        for attribute in dir(klass):
            if attribute not in args and not mock._is_magic(attribute):
                func = mock.patch.object(klass, attribute, mock_class())(func)
        return func
    return first_wrap

def _patch_except_model(klass, *args, **kwargs):
    return patch_except(klass, "_meta", *args, **kwargs)

patch_except.model = _patch_except_model
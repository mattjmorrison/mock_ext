import mock
from mock import patch, MagicMock

class Mock(mock.Mock):

    missing_return_value = "'%s' was expected to return but '%s' was found"
    missing_from_chain = "%s not found in the call chain"

    def assert_chained(self, call_chain, value=None):
        if self._get_method_calls(self):
            obj = self
        else:
            obj = self.return_value
        return self._assert_chained(obj, call_chain, value)

    def _assert_chained(self, mock_object, call_chain, value):
        calls = self._get_method_calls(mock_object)
        for mock_call in calls:
            for method_call_number, method_call in enumerate(call_chain):
                if method_call == mock_call:
                    if not isinstance(mock_call, (mock.callargs, str)):
                        return True
                    else:
                        new_call_chain = self._get_call_chain(call_chain, method_call_number)
                        return_value = self._get_return_value(method_call, mock_object)
                        if not new_call_chain:
                            return self._handle_end_of_chain(return_value, value)
                        if self._assert_chained(return_value, new_call_chain, value):
                            return True

        raise AssertionError(self.missing_from_chain % call_chain)

    def _get_method_calls(self, mock_object):
        calls_and_properties = []
        calls = mock_object.method_calls
        for call in calls:
            if '.' not in call[0]:
                calls_and_properties.append(call)

        return calls_and_properties + mock_object._children.keys()

    def _get_return_value(self, method_call, mock_object):
        if '.' in method_call[0]:
            return_value = mock_object
            for node in method_call[0].split('.'):
                return_value = getattr(return_value, node)
            return_value = return_value.return_value
        else:
            if isinstance(method_call, (tuple, mock.callargs)):
                return_value = getattr(mock_object, method_call[0]).return_value
            else:
                return_value = getattr(mock_object, method_call)
        return return_value

    def _get_call_chain(self, call_chain, method_call_number):
        return call_chain[0:method_call_number] + call_chain[method_call_number + 1:]

    def _handle_end_of_chain(self, return_value, value):
        if value == return_value:
            return True
        else:
            raise AssertionError(self.missing_return_value % (value, return_value))

def patch_exclude(klass, *args, **kwargs):
    mock_class = kwargs.get('with_mock', Mock)

    def first_wrap(func):
        for attribute in dir(klass):
            if attribute not in args and not mock._is_magic(attribute):
                func = mock.patch.object(klass, attribute, mock_class())(func)
        return func
    return first_wrap

def _patch_exclude_model(klass, *args, **kwargs):
    return patch_exclude(klass, '_meta', *args, **kwargs)

mock.patch.exclude = patch_exclude
mock.patch.exclude.model = _patch_exclude_model
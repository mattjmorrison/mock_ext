import unittest
import mock

from mock_ext import patch_except

class AgeMissing(ValueError):
    pass

class NameMissing(ValueError):
    pass

class AddressMissing(ValueError):
    pass

class DummyDjangoModel(object):
    _meta = "Meta"

    def something(self):
        pass

class MyThing(object):
    def __init__(self):
        self.name = None
        self.age = None
        self.address = None
        self.things = 0

    def do_something(self, *args, **kwargs):
        self.set_name(**kwargs)
        self.set_age(**kwargs)
        self.set_address(**kwargs)
        self.add(1)

    def set_address(self, **kwargs):
        self.add(1)
        if 'address' in kwargs:
            self.address = kwargs['address']
        else:
            raise AddressMissing

    def add(self, number):
        self.things+=number

    def set_name(self, **kwargs):
        if 'name' in kwargs:
            self.name = kwargs['name']
        else:
            raise NameMissing("name is required")

    def set_age(self, **kwargs):
        if 'age' in kwargs:
            self.age = kwargs['age']
        else:
            raise AgeMissing

    def get_something(self):
        return "Something"


class PatchExceptTests(unittest.TestCase):

    def setUp(self):
        self.thing = MyThing()

    def test_name_is_required(self):
        self.assertRaises(NameMissing, self.thing.set_name)

    def test_sets_name(self):
        self.thing.set_name(name="Matt")
        self.assertEqual("Matt", self.thing.name)

    def test_age_is_required(self):
        self.assertRaises(AgeMissing, self.thing.set_age)

    def test_sets_age(self):
        self.thing.set_age(age=12)
        self.assertEqual(12, self.thing.age)

    def test_sets_address(self):
        self.thing.set_address(address="abc 123")
        self.assertEqual("abc 123", self.thing.address)

    def test_address_is_required(self):
        self.assertRaises(AddressMissing, self.thing.set_address)

    def test_something_does_everything(self):
        self.thing.do_something()
        self.assertEqual(1, self.thing.things)
    test_something_does_everything = mock.patch.object(MyThing, 'set_name', mock.Mock())(test_something_does_everything)
    test_something_does_everything = mock.patch.object(MyThing, 'set_age', mock.Mock())(test_something_does_everything)
    test_something_does_everything = mock.patch.object(MyThing, 'set_address', mock.Mock())(test_something_does_everything)

    @patch_except(MyThing, 'do_something', 'add')
    def test_something_does_everything_new_mock(self):
        self.thing.do_something()
        self.assertEqual(1, self.thing.things)

    @patch_except(MyThing, 'do_something', 'set_name', 'add')
    def test_sets_name_and_things(self):
        self.thing.do_something(name="matt")
        self.assertEqual(1, self.thing.things)
        self.assertEqual(self.thing.name, 'matt')

    @patch_except(MyThing, 'do_something', 'set_address', 'add')
    def test_sets_address_and_things(self):
        self.thing.do_something(address="xxx")
        self.assertEqual(2, self.thing.things)
        self.assertEqual(self.thing.address, 'xxx')

    @patch_except(MyThing, 'do_something', with_mock=mock.MagicMock)
    def test_sets_address_and_things(self):
        self.thing.do_something()
        self.assertTrue(isinstance(self.thing.get_something(), mock.MagicMock))

class PatchExceptModelTests(unittest.TestCase):

    @patch_except.model(DummyDjangoModel, 'something')
    def test_does_not_patch_meta_for_django_models(self):
        model = DummyDjangoModel()
        self.assertEqual('Meta', model._meta)


if __name__ == '__main__':
    unittest.main()
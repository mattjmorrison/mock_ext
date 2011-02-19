import unittest
import mock_ext

class AgeMissing(ValueError):
    pass

class NameMissing(ValueError):
    pass

class AddressMissing(ValueError):
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

    def nested_method_calls(self, stuff):
        return self.nested_call_one().first(stuff).second(stuff).third(123)

    def nested_call_one(self):
        return self

    def first(self):
        return self

    def second(self):
        return self

class SomeTests(unittest.TestCase):

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
    test_something_does_everything = mock_ext.patch.object(MyThing, 'set_name', mock_ext.Mock())(test_something_does_everything)
    test_something_does_everything = mock_ext.patch.object(MyThing, 'set_age', mock_ext.Mock())(test_something_does_everything)
    test_something_does_everything = mock_ext.patch.object(MyThing, 'set_address', mock_ext.Mock())(test_something_does_everything)

    @mock_ext.patch.exclude(MyThing, 'do_something', 'add')
    def test_something_does_everything_new_mock(self):
        self.thing.do_something()
        self.assertEqual(1, self.thing.things)

    @mock_ext.patch.exclude(MyThing, 'do_something', 'set_name', 'add')
    def test_sets_name_and_things(self):
        self.thing.do_something(name="matt")
        self.assertEqual(1, self.thing.things)
        self.assertEqual(self.thing.name, 'matt')

    @mock_ext.patch.exclude(MyThing, 'do_something', 'set_address', 'add')
    def test_sets_address_and_things(self):
        self.thing.do_something(address="xxx")
        self.assertEqual(2, self.thing.things)
        self.assertEqual(self.thing.address, 'xxx')

    @mock_ext.patch.exclude(MyThing, 'do_something', with_mock=mock_ext.MagicMock)
    def test_sets_address_and_things(self):
        self.thing.do_something()
        self.assertTrue(isinstance(self.thing.get_something(), mock_ext.MagicMock))

    @mock_ext.patch.exclude(MyThing, 'nested_method_calls', with_mock=mock_ext.Mock)
    def test_chained_calls(self):
        result = self.thing.nested_method_calls("abc")

        self.thing.nested_call_one.assertChained([
            ('third', (123,), {}),
            ('first', ("abc",), {}),
            ('second', ("abc",), {}),
        ], result)

class SampleManager(object):
    @property
    def base_query(self):
        pass

    def filter(self):
        pass

    def some_other_chained_call(self):
        return self.base_query.filter(one=1, two=2).filter(three=3).filter(three=3)

    def some_chained_call(self):
        return self.base_query.filter(one=1).filter(two=2).filter(three=3).filter(three=3)

class Other(unittest.TestCase):

    def test_chained_calls_and_properties_with_return_value(self):
        manager = mock_ext.Mock(spec=SampleManager)
        result = SampleManager.some_other_chained_call(manager)
        manager.assertChained([
            'base_query',
            ('filter', (), {'one':1, 'two':2}),
            ('filter', (), {'three':3}),
            ('filter', (), {'three':3}),
        ], result)

if __name__ == '__main__':
    unittest.main()
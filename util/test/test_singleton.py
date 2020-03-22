import unittest
from .. import Singleton

@Singleton
class TestClass:

    def __init__(self, some_var):
        self.some_var = some_var

    def get(self):
        return self.some_var

class TestSingleton(unittest.TestCase):

    def test_instantiation_params(self):
        instance = TestClass.instance(123)
        self.assertEqual(instance.get(), 123)

        instance = TestClass.instance(124)
        self.assertEqual(instance.get(), 124)
        old_instance = instance

        instance = TestClass.instance(124)
        self.assertEqual(instance.get(), 124)
        self.assertEqual(instance, old_instance)

        instance = TestClass.instance(125)
        self.assertEqual(instance.get(), 125)

    def test_cant_construct(self):
        with self.assertRaises(TypeError):
            test = TestClass()

    def test_instancecheck(self):
        instance = TestClass.instance(123)
        self.assertIsInstance(instance, TestClass)


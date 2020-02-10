from django.test import TestCase

from serializer import serializers
from serializer.tests.models import BasicModel, ModelChild, ModelSimpleParent


class BasicSerializer(serializers.Serializer):
    class Meta:
        model = BasicModel
        fields = ['name']


class TestSerializer(TestCase):

    def test_has_correct_attributes(self):
        basic_expected = BasicSerializer()

        expected_fields = ['name']

        self.assertEqual(BasicModel, basic_expected.model)
        self.assertEqual(expected_fields, basic_expected.fields)

    def test_single_normal_serialization(self):
        basic_instance = BasicModel.objects.create(name="Basic")
        serializer = BasicSerializer(basic_instance)

        expected = [
            {'name': 'Basic'}
        ]

        result = serializer.serialize(mode="normal")

        self.assertEqual(expected, result)

    def test_multiple_normal_serialization(self):
        BasicModel.objects.create(name="Basic")
        BasicModel.objects.create(name="Basic2")

        serializer = BasicSerializer()

        expected = [
            {'name': 'Basic'},
            {'name': 'Basic2'}
        ]

        result = serializer.serialize(mode="normal")

        self.assertEqual(expected, result)

    def test_invalid_serialization_mode(self):
        serializer = BasicSerializer()

        with self.assertRaises(Exception):
            serializer.serialize('mode invalid')

    def test_single_split_serialization(self):
        basic_instance = BasicModel.objects.create(name="Basic")
        serializer = BasicSerializer(basic_instance)

        expected = {
            'model': ['name'],
            'data': [['Basic']]
        }

        result = serializer.serialize(mode="split")

        self.assertEqual(expected, result)

    def test_multiple_split_serialization(self):
        BasicModel.objects.create(name="Basic")
        BasicModel.objects.create(name="Basic2")

        serializer = BasicSerializer()

        expected = {
            'model': ['name'],
            'data': [['Basic'], ['Basic2']]
        }

        result = serializer.serialize(mode="split")

        self.assertEqual(expected, result)

    def test_single_normal_creation(self):
        serializer = BasicSerializer()

        obj_data = {'name': 'TestCreation'}

        serializer.create(obj_data, 'normal')

        all_objs = BasicModel.objects.all()
        first = all_objs.first()

        self.assertEqual(len(all_objs), 1)
        self.assertEqual(first.name, 'TestCreation')

    def test_multiple_normal_creation(self):
        serializer = BasicSerializer()

        obj_data = [
            {'name': 'TestCreation'},
            {'name': 'TestCreation2'},
        ]
        serializer.create(obj_data, 'normal')

        all_objs = BasicModel.objects.all()
        first = all_objs[0]
        second = all_objs[1]

        self.assertEqual(len(all_objs), 2)
        self.assertEqual(first.name, 'TestCreation')
        self.assertEqual(second.name, 'TestCreation2')

    def test_creation_invalid(self):
        serializer = BasicSerializer()

        obj_data = {'na': 'TestCreation'}

        with self.assertRaises(Exception):
            serializer.create(obj_data, 'normal')

        all_objs = BasicModel.objects.all()
        self.assertEqual(len(all_objs), 0)

    def test_single_split_creation(self):
        serializer = BasicSerializer()

        obj_data = {
            'model': ['name'],
            'data': [['TestSplitCreation']]
        }

        serializer.create(obj_data, 'split')

        all_objs = BasicModel.objects.all()
        first = all_objs.first()

        self.assertEqual(len(all_objs), 1)
        self.assertEqual(first.name, 'TestSplitCreation')

    def test_multiple_split_creation(self):
        serializer = BasicSerializer()

        obj_data = {
            'model': ['name'],
            'data': [
                ['TestSplitCreation'],
                ['TestSplitCreation2Two'],
            ]
        }

        serializer.create(obj_data, 'split')

        all_objs = BasicModel.objects.all()
        first = all_objs[0]
        second = all_objs[1]

        self.assertEqual(len(all_objs), 2)
        self.assertEqual(first.name, 'TestSplitCreation')
        self.assertEqual(second.name, 'TestSplitCreation2Two')

    def test_invalid_split_creation(self):
        serializer = BasicSerializer()

        obj_data = {
            'model': ['nam'],
            'data': [['TestSplitCreation']]
        }

        with self.assertRaises(Exception):
            serializer.create(obj_data, 'split')

        all_objs = BasicModel.objects.all()

        self.assertEqual(len(all_objs), 0)


# Representation tests


class CustomBasicSerializer(serializers.Serializer):

    def representation_name(self, name):
        return f'{name}_representation'

    class Meta:
        model = BasicModel
        fields = ['name']


class TestCustomSerializer(TestCase):

    def test_single_normal_serialization(self):
        basic_instance = BasicModel.objects.create(name="Model")
        serializer = CustomBasicSerializer(basic_instance)

        expected = [
            {'name': 'Model_representation'}
        ]

        result = serializer.serialize(mode="normal")

        self.assertEqual(expected, result)

    def test_single_split_serialization(self):
        basic_instance = BasicModel.objects.create(name="Model")
        serializer = CustomBasicSerializer(basic_instance)

        expected = {
            'model': ['name'],
            'data': [['Model_representation']]
        }

        result = serializer.serialize(mode="split")

        self.assertEqual(expected, result)


# Relations tests


class ParentSimpleSerializer(serializers.Serializer):
    class Meta:
        model = ModelSimpleParent
        fields = ['name']


class ChildSerializer(serializers.Serializer):
    related = ParentSimpleSerializer

    class Meta:
        model = ModelChild
        fields = ['name', 'related']


class TestRelationsSerializer(TestCase):

    def test_single_normal_serialization(self):
        parent = ModelSimpleParent.objects.create(name='Parent')
        child = ModelChild.objects.create(name='Child', related=parent)

        child_serializer = ChildSerializer(child)

        expected = [
            {
                'name': 'Child',
                'related': 1
            }
        ]

        result = child_serializer.serialize('normal')

        self.assertEqual(expected, result)

    def test_multiple_normal_serialization(self):
        parent = ModelSimpleParent.objects.create(name='Parent')
        parent2 = ModelSimpleParent.objects.create(name='Parent')

        ModelChild.objects.create(name='ChildParent', related=parent)
        ModelChild.objects.create(name='ChildParent2', related=parent2)
        ModelChild.objects.create(name='Child2Parent2', related=parent2)

        child_serializer = ChildSerializer()

        expected = [
            {
                'name': 'ChildParent',
                'related': 1
            },
            {
                'name': 'ChildParent2',
                'related': 2
            },
            {
                'name': 'Child2Parent2',
                'related': 2
            }
        ]

        result = child_serializer.serialize('normal')

        self.assertEqual(expected, result)

    def test_single_split_serialization(self):
        parent = ModelSimpleParent.objects.create(name='Parent')
        child = ModelChild.objects.create(name='Child', related=parent)

        child_serializer = ChildSerializer(child)

        expected = {
            'model': ['name', 'related'],
            'data': [['Child', 1]]
        }

        result = child_serializer.serialize('split')
        self.assertEqual(expected, result)

    def test_multiple_split_serialization(self):
        parent = ModelSimpleParent.objects.create(name='Parent')
        parent2 = ModelSimpleParent.objects.create(name='Parent')

        ModelChild.objects.create(name='ChildParent', related=parent)
        ModelChild.objects.create(name='ChildParent2', related=parent2)
        ModelChild.objects.create(name='Child2Parent2', related=parent2)

        child_serializer = ChildSerializer()

        expected = {
            'model': ['name', 'related'],
            'data': [
                ['ChildParent', 1],
                ['ChildParent2', 2],
                ['Child2Parent2', 2]
            ]
        }

        result = child_serializer.serialize('split')

        self.assertEqual(expected, result)

    def test_single_normal_creation(self):
        child_serializer = ChildSerializer()

        data = {
            'name': 'ChildName',
            'related': {
                'name': 'ParentName'
            }
        }

        child_serializer.create(data, 'normal')

        child_objs = ModelChild.objects.all()
        parent_objs = ModelSimpleParent.objects.all()

        child_first = child_objs.first()
        parent_first = parent_objs.first()

        self.assertEqual(len(child_objs), 1)
        self.assertEqual(child_first.name, 'ChildName')

        self.assertEqual(len(parent_objs), 1)
        self.assertEqual(parent_first.name, 'ParentName')

    # def test_single_normal_serialization_with_related(self):
    #     parent = ModelSimpleParent.objects.create(name='Parent')
    #     child = ModelChild.objects.create(name='Child', related=parent)
    #
    #     child_related_serializer = ChildSerializer(child)
    #
    #     expected = [
    #         {
    #             'name': 'Child',
    #             'related': {
    #                 'name'
    #             }
    #         }
    #     ]
    #
    #     result = child_related_serializer.serialize('normal')
    #
    #     self.assertEqual(expected, result)

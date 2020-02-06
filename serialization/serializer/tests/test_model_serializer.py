from django.test import TestCase

from serializer import serializers



# model_serializer = ModelSerializerTest()
#
# model_serializer_related = ModelSerializerRelated(
#     related_to={'related_model': model_serializer}
# )
#
# model_serializer_related_to_other = ModelSerializerRelatedToOther(
#     related_to={'related_model': model_serializer_related}
# )
# model_serializer_related_to_another = ModelSerializerRelatedToAnother(
#     related_to={'related_model': model_serializer_related}
# )
from serializer.tests.models import BasicModel


class BasicSerializer(serializers.Serializer):
    class Meta:
        model = BasicModel
        fields = ['name']


class TestSerializer(TestCase):

    def test_has_correct_attributes(self):
        expected_fields = ['name']
        expected_related = {}

        basic_expected = BasicSerializer()

        self.assertEqual(BasicModel, basic_expected.model)
        self.assertEqual(expected_fields, basic_expected.fields)
        self.assertEqual(expected_related, basic_expected.serializer_related)

    def test_invalid_serialization_mode(self):
        serializer = BasicSerializer()

        with self.assertRaises(Exception):
            serializer.serialize('mode invalid')

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

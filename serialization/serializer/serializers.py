from builtins import print
from collections import Iterable
from itertools import chain


class SerializerMeta(type):

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        meta = attrs.pop('Meta', None)
        model = getattr(meta, 'model', None)
        fields = getattr(meta, 'fields', None)

        foo = {}
        if model and fields:
            foo = mcs._get_foo(model, fields, attrs)

        setattr(new_class, 'model', model)
        setattr(new_class, 'fields', fields)
        setattr(new_class, 'foo', foo)

        return new_class

    @classmethod
    def _get_foo(mcs, model, fields, attrs):
        foo = {}
        for field in fields:
            representation_name = f'representation_{field}'
            representation_func = attrs.pop(representation_name, None)

            serializer_related = attrs.pop(field, None)

            foo[field] = {
                'model_field': mcs._get_model_field(model, field),
                'representation': representation_func,
                'serializer': {
                    'class': serializer_related,
                    'instance': None
                }
            }

        return foo

    @classmethod
    def _get_model_field(mcs, model, field_name):
        model_meta = model._meta
        model_fields = list(model_meta.concrete_fields) + list(model_meta.private_fields)   # EveryTime

        for field in model_fields:
            if field.name == field_name:
                return field

        raise Exception(f'{field_name} does not reference a field of {model}')

    @classmethod
    def _get_serializer_fields(mcs, fields, values):
        serializer_related = {}

        for i in range(len(fields)):
            serializer_related[fields[i]] = {
                'class': values[i],
                'instance': None
            }
        return serializer_related

    '''
    field   => 
        -> model_field
        -> representation_func

    field   => serializer_related
        >> class
        >> instance
    '''


MODEL = 'model'
DATA = 'data'


class Serializer(metaclass=SerializerMeta):

    def __init__(self, initial_data=None, related_to=None):
        self.data = self.get_iterable_initial_data(initial_data)
        self.model_fields = self.get_model_fields()

    def get_iterable_initial_data(self, initial_data) -> Iterable:
        if isinstance(initial_data, Iterable):
            return initial_data

        if initial_data:
            return [initial_data]

        return self.model.objects.all()

    def get_model_fields(self):
        model_meta = self.model._meta
        model_fields = list(model_meta.concrete_fields) + list(model_meta.private_fields)

        return model_fields

    def serialize(self, mode):
        function_name = f'{mode}_serialization'
        if hasattr(self, function_name):    #########
            return getattr(self, function_name)()

        raise Exception('Invalid serialization mode')

    def normal_serialization(self) -> list:
        all_obj_data = [self.to_dict(obj) for obj in self.data]
        return all_obj_data

    def split_serialization(self) -> dict:
        all_obj_data = [self.get_field_values(obj) for obj in self.data]
        return {
            MODEL: self.fields,
            DATA: all_obj_data
        }

    def to_dict(self, instance_model):
        dict_model = {}

        for field in self.fields:
            value_str = self.foo[field]['model_field'].value_from_object(instance_model)

            custom_representation = self.foo[field]['representation']
            if custom_representation:
                value_str = custom_representation(self, value_str)

            dict_model[field] = value_str

        return dict_model

    def get_field_values(self, instance_model):
        field_values = []

        for field in self.fields:
            value_str = self.foo[field]['model_field'].value_from_object(instance_model)

            custom_representation = self.foo[field]['representation']
            if custom_representation:
                value_str = custom_representation(self, value_str)

            field_values.append(value_str)

        return field_values

    def create(self, obj_data, mode):
        function_name = f'{mode}_creation'
        if hasattr(self, function_name):
            return getattr(self, function_name)(obj_data)

        raise Exception('Invalid creation mode')

    def normal_creation(self, obj_data):
        data_type = type(obj_data)

        if data_type == dict:
            self.create_single_instance(obj_data)
        elif data_type == list:
            self.create_multiple_instances(obj_data)

    def create_single_instance(self, obj_data: dict):
        obj_fields = list(obj_data.keys())

        if obj_fields != self.fields:
            raise Exception("Invalid Data, Keys must be the model fields")

        data_to_create = {}

        for field in self.fields:
            serializer_related = self.foo[field]['serializer']
            if serializer_related['class']:
                data_to_create[field] = self.create_instance(serializer_related['class'].model, obj_data[field])
            else:
                data_to_create[field] = obj_data[field]

        return self.create_instance(self.model, data_to_create)

    @staticmethod
    def create_instance(model, obj_data):
        return model.objects.create(**obj_data)

    def create_multiple_instances(self, obj_data: list):
        for obj in obj_data:
            self.create_single_instance(obj)

    def split_creation(self, obj_data: dict):
        fields_model = obj_data.pop(MODEL, None)
        data = obj_data.pop(DATA, None)

        self.assert_fields_model_valid(fields_model)
        self.assert_data_is_valid(data)

        self.form_data_and_create(fields_model, data)

    def assert_fields_model_valid(self, fields_model):
        if fields_model is None:
            raise Exception(f'´{MODEL}´ field must be informed')

        if fields_model != self.fields:
            raise Exception(f"Invalid ´{MODEL}´, Keys must be the model fields")

    def assert_data_is_valid(self, data):
        if data is None:
            raise Exception(f'´{DATA}´ field must be informed')

        if not isinstance(data, Iterable):
            raise Exception(f'´{DATA}´ field must be an Iterable')

    def form_data_and_create(self, fields_model, data):
        data_to_create = {}
        fields_model_size = len(fields_model)

        for specific_obj in data:

            for i in range(fields_model_size):
                data_to_create[fields_model[i]] = specific_obj[i]

            self.model.objects.create(**data_to_create)

    def get_model_name(self) -> str:
        return self.model.__name__

    def remove_objects(self, objs_to_remove):
        self.data = self.data.exclude(id__in=objs_to_remove)

    def get_serializer_related_names(self) -> list:
        related_names = []

        for data in self.serializer_related.values():
            # related_name = ModelUtils.get_class_name(data['instance'])
            # related_names.append(related_name)
            pass

        return related_names

    def get_serializer_related_model_names(self) -> list:
        related_names = []

        for data in self.serializer_related.values():
            related_model_name = data['instance'].get_model_name()
            related_names.append(related_model_name)

        return related_names

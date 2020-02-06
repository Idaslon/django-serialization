from collections import Iterable
from itertools import chain


class SerializerMeta(type):

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        meta = attrs.pop('Meta', None)
        model = getattr(meta, 'model', None)
        fields = getattr(meta, 'fields', None)
        related_to = getattr(meta, 'related_to', None)

        serializer_related = {}

        if related_to:
            serializer_related = mcs._get_serializer_related(
                list(related_to.keys()),
                list(related_to.values())
            )

        setattr(new_class, 'model', model)
        setattr(new_class, 'fields', fields)
        setattr(new_class, 'serializer_related', serializer_related)

        return new_class

    @classmethod
    def _get_serializer_related(mcs, fields, values):
        serializer_related = {}

        for i in range(len(fields)):
            serializer_related[fields[i]] = {
                'class': values[i],
                'instance': None
            }
        return serializer_related


MODEL = 'model'
DATA = 'data'


class Serializer(metaclass=SerializerMeta):

    def __init__(self, initial_data=None, related_to=None):
        self.data = self.get_iterable_initial_data(initial_data)
        self.model_fields = self.get_model_fields()

        if related_to:
            self._set_related(related_to)

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

    def _set_related(self, related_to):
        for field, instance in related_to.items():
            self.serializer_related[field]['instance'] = instance

    def serialize(self, mode):
        function_name = f'{mode}_serialization'
        if hasattr(self, function_name):
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

        for field in self.model_fields:
            field_name = field.name

            if field_name in self.fields:
                value_str = str(field.value_from_object(instance_model))
                dict_model[field_name] = value_str

        return dict_model

    def get_field_values(self, instance_model):
        field_values = []

        for field in self.model_fields:
            field_name = field.name

            if field_name in self.fields:
                value_str = str(field.value_from_object(instance_model))
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

        self.model.objects.create(**obj_data)

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
        for specific_obj in data:

            for i in range(len(fields_model)):
                data_to_create[fields_model[i]] = specific_obj[i]

            self.model.objects.create(**data_to_create)

    def get_model_name(self) -> str:
        return self.model.__name__

    def get_objects_count(self) -> int:
        return len(self.data)

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

import pytest


@pytest.fixture(autouse=True, scope='session')
def __make_unmanaged_managed():
    from django.apps import apps

    get_models = apps.get_models
    print('asd')

    for m in [m for m in get_models() if not m._meta.managed]:
        m._meta.managed = True

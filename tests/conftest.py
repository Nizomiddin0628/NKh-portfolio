import pytest


@pytest.fixture
def seeded(db):
    from django.core.management import call_command
    call_command("seed", verbosity=0)

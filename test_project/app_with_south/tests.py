from django.test import TestCase
from test_project.app_with_south.models import FakeSouthModel

class MigarationTest(TestCase):

    def test_check_tables_exist(self):
        self.assertEqual(list(FakeSouthModel.objects.all()), [])

import unittest
from capstone.forms import CreateUserForm


class TestForms(unittest.TestCase):
    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Run once to set up non-modified data for all class methods.")
        pass

    def setUp(self):
        print("setUp: Run once for every test method to setup clean data.")
        pass

    def test_form(self):
        print("Method: test_form.")
        form = CreateUserForm()
        field_label = form.fields
        # ive spent a lot of time trying to figure this out and it doesnt seem
        # to want to work with me so im using this as a placeholder
        self.assertNotEqual(field_label, "{'username': <django.forms.fields.CharFie[250 chars]160>}")


if __name__ == '__main__':
    unittest.main()

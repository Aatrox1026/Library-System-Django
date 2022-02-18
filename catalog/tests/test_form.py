from django.test import TestCase
from datetime import date, timedelta
from catalog.form import RenewBookForm


class RenewBookFormTest(TestCase):
    def test_renew_form_date_field_label(self):
        form = RenewBookForm()
        self.assertTrue(form.fields['renewal_date'].label is None or form.fields['renewal_date'].label == 'renewal_date')

    def test_renew_form_date_field_help_text(self):
        form = RenewBookForm()
        self.assertEqual(form.fields['renewal_date'].help_text, 'Enter a date between now and 4 weeks (default 3).')

    def test_renew_form_date_in_past(self):
        past_date = date.today() - timedelta(days=1)
        form_data = {'renewal_date': past_date}
        form = RenewBookForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_renew_form_date_too_far_in_future(self):
        future_date = date.today() + timedelta(weeks=5)
        form_data = {'renewal_date': future_date}
        form = RenewBookForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_renew_form_date_today(self):
        today = date.today()
        form_data = {'renewal_date': today}
        form = RenewBookForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_renew_form_date_max(self):
        max_date = date.today() + timedelta(weeks=4)
        form_data = {'renewal_date': max_date}
        form = RenewBookForm(data=form_data)
        self.assertTrue(form.is_valid())

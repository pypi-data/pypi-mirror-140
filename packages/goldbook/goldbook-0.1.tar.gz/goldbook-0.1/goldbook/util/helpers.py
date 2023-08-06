from django.utils.timezone import datetime
from django.core.exceptions import ValidationError



def my_year_validator(value):
    if value < 1900 or value > datetime.now().year:
        raise ValidationError(
            _('%(value)s is not a valid year'),
            params={'value': value},
        )

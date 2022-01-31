from django.core.exceptions import ValidationError


def username_validator(username):
    if username == 'me':
        raise ValidationError('Name "me" is required for system needs')

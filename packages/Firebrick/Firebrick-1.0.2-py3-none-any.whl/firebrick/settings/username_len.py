from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import User
from django.conf import settings


try:
    USERNAME_LENGTH_MIN = settings.USERNAME_LENGTH_MIN
except AttributeError:
    raise AttributeError("'USERNAME_LENGTH_MIN' variable needs to be set in settings.py file")
USERNAME_LENGTH_MAX = 16
try:
    USERNAME_LENGTH_MAX = settings.USERNAME_LENGTH_MAX
except AttributeError:
    raise AttributeError("'USERNAME_LENGTH_MAX' variable needs to be set in settings.py file")
try:
    USERNAME_VALID_CHARS = settings.USERNAME_VALID_CHARS
except AttributeError:
    raise AttributeError("'USERNAME_VALID_CHARS' variable needs to be set in settings.py file")
# getting username field
username = User._meta.get_field("username")
username.max_length = USERNAME_LENGTH_MAX
for v in username.validators:
    if isinstance(v, MaxLengthValidator):
        # changing max username length value
        v.limit_value = USERNAME_LENGTH_MAX
    if isinstance(v, UnicodeUsernameValidator):
        # removing default valid char check
        username.validators.remove(v)
# adding min length validator to the username field
username.validators.append(MinLengthValidator(USERNAME_LENGTH_MIN))
# adding a validator to check that the username only contains valid chars
username.validators.append(RegexValidator(USERNAME_VALID_CHARS, 
                                            message='Enter a valid username. A username may contain only letters, numbers, and _ characters.'))
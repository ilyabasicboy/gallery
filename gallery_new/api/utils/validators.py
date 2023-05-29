from django.core.validators import RegexValidator
from .exceptions import MailformedData
import re


class MimeTypeValidator(RegexValidator):

    regex = '\w+/[-.\w]+(?:\+[-.\w]+)?'

    """
        Check mime type validity using regex
    """

    def __call__(self, value):

        """ Customized method to raise MailformedData """

        regex_matches = self.regex.search(str(value))
        invalid_input = regex_matches if self.inverse_match else not regex_matches
        if invalid_input:
            raise MailformedData


def validate_name(old_name: str) -> str:
    invalid_characters = r"\/\|\[\]\(\)\"\'\`\{\}\<\>"
    new_name = str(old_name).strip().lower()

    if not new_name:
        return '_'

    new_name = re.sub(invalid_characters, '', new_name)
    return new_name
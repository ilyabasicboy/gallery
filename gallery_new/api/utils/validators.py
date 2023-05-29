from django.core.validators import RegexValidator
from .exceptions import MailformedData


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
from django.contrib.auth.tokens import default_token_generator
from templated_mail.mail import BaseEmailMessage

from core.utils import encode_uid
from core.constant import ACTIVATION_URL

class ActivationEmail(BaseEmailMessage):
    template_name = "email/activate.html"

    def get_context_data(self):
        context = super().get_context_data()

        user = context.get("user")
        context["uid"] = encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = ACTIVATION_URL.format(**context)
        return context


class ConfirmationEmail(BaseEmailMessage):
    template_name = "email/confirmation.html"



from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_field, user_username

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Permite que los usuarios se registren automáticamente sin necesidad de confirmación.
        """
        return True

    def populate_user(self, request, sociallogin, data):
        """
        Auto completa los datos del usuario para evitar la pantalla de registro adicional.
        """
        user = sociallogin.user
        user_email = data.get("email")
        user_name = data.get("name") or data.get("given_name")

        if user_email:
            user_field(user, "email", user_email)

        if user_name:
            user_field(user, "first_name", user_name)

        # Si no tiene username, lo generamos basado en el email
        if not user_username(user):
            user_field(user, "username", user_email.split("@")[0])

        return user

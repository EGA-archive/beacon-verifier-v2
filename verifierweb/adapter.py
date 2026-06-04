from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class MyOIDCAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        token = getattr(sociallogin, "token", None)

        if token:
            sociallogin.account.extra_data["access_token"] = getattr(token, "token", None)
            sociallogin.account.extra_data["id_token"] = getattr(token, "id_token", None)
            sociallogin.account.extra_data["refresh_token"] = getattr(token, "refresh_token", None)
            #print(sociallogin, flush=True)
            sociallogin.account.save()

            #print(sociallogin.account.extra_data["access_token"])


        return super().pre_social_login(request, sociallogin)
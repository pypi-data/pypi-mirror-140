from django.core.management.base import BaseCommand, CommandError
from firebrick.templates.templating import GenerateFromTemplate, TemplateFromFiles
from click import echo


class Command(BaseCommand):
    help = 'Creates a firebrick accounts app in your django project.'
    
    def handle(self, *args, **options):
        GenerateFromTemplate(
            [
                TemplateFromFiles('accounts', base_local_path='accounts')
            ]
        )
        echo(f'''
Accounts app made.
Make sure to add the following to 'INSTALLED_APPS' in settings.py file:
 - 'crispy_forms',
 - 'accounts.apps.AccountsConfig',
Also add at the bottom of the settings.py file:
 - CRISPY_TEMPLATE_PACK = 'bootstrap4'
 - USERNAME_VALID_CHARS = '^[0-9a-zA-Z_]*$'
 - USERNAME_LENGTH_MIN = 3
 - USERNAME_LENGTH_MAX = 16
 
And add the following to your projects main urls.py file:
 - from django.contrib.auth import views as auth_views
 - from accounts import views as accounts_views

And add the following to 'urlpatterns' in your projects main urls.py file:
 - path('register/', accounts_views.register, name='register'),
 - path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
 - path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
''')
import os
from celery import Celery

#set enviromenrt var for the settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')

#create the app 
app = Celery('rfiq')

# we are gone load the config of celery from settings
# with the namespace CELERY which means every config in settings start with 
# CELERY_ will be loaded

app.config_from_object('django.conf:settings',namespace='CELERY')

#load all tasks from all registered apps (INSTALLED_APPS)
app.autodiscover_tasks()







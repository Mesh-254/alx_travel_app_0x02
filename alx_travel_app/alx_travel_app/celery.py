from celery import Celery
import os

# Set the default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')


app = Celery('alx_travel_app', broker='pyamqp://guest@localhost//', backend='rpc://')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')

# Explicitly auto-discover tasks
app.autodiscover_tasks()

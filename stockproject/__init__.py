#"Import Celery app from celery.py"
#Without this:Celery app may never initialize.Then:tasks not discovered
from  .celery import app as celery_app
__all__ = ('celery_app',)
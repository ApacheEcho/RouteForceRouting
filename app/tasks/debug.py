from app.celery import celery

@celery.task
def boom_task():
    1/0

from app.celery_worker import celery

@celery.task
def boom_task():
    1/0

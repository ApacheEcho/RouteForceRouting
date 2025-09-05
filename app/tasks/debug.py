from app.celery_app import celery


@celery.task
def boom_task():
    1 / 0

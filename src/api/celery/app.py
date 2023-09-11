from celery import Celery

from src.api.config import settings


class Config:
    enable_utc = True
    timezone = 'Europe/Moscow'
    broker_url = '{}://{}:{}@{}:{}/{}'.format(
        'amqp',
        settings.RABBITMQ_DEFAULT_USER,
        settings.RABBITMQ_DEFAULT_PASS,
        settings.RABBITMQ_SERVER,
        settings.RABBITMQ_PORT,
        settings.RABBITMQ_DEFAULT_VHOST,
    )
    broker_connection_retry_on_startup = False
    result_backend = 'rpc://'
    worker_send_task_event = False
    task_ignore_result = True
    # task will be killed after 60 seconds
    task_time_limit = 60
    # task will raise exception SoftTimeLimitExceeded after 50 seconds
    task_soft_time_limit = 50
    # task messages will be acknowledged after the task has been executed, not just before (the default behavior).
    task_acks_late = True
    # One worker taks 10 tasks from queue at a time and will increase the performance
    worker_prefetch_multiplier = 10


app_celery = Celery(__name__)
app_celery.config_from_object(Config)

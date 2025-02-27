import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.env_dev')
django.setup()

from celery.signals import worker_ready
from celery import Celery
from celery.schedules import crontab
from apps.products.services_spider import SpiderProductAPI
from apps.products.services_mongo import MongoProcessor
from apps.products.services_es import ESProcessor
from apps.products.services_neo4j import Neo4jProcessor
from apps.commons.tools import CommonTools
import logging
import jsonpickle

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='MQ')
app.autodiscover_tasks()

logger = logging.getLogger(__name__)

app.conf.beat_schedule = {
    'es-add-index-every-hour': {
        'task': 'tasks.task_es_add_index',
        'schedule': crontab(minute=0, hour="*/1")
    },
    'neo4j-add-order-every-hour': {
        'task': 'tasks.task_neo4j_add_order',
        'schedule': crontab(minute=0, hour="*/1")
    }
}
app.conf.timezone = 'US/Eastern'

@worker_ready.connect
def at_start(sender, **kwargs):
    """Run tasks at startup"""
    # CommonTools.postgres_init()
    # CommonTools.redis_init()
    # ESProcessor.create_mapping()
    # ESProcessor.delete_all_index()
    # MongoProcessor.delete_all_products()
    # SpiderProductAPI.async_spider.delay()

@app.task
def task_es_add_index():
    res_array = ESProcessor.add_index_from_mongo()
    logger.info("[sync product from mongo to es] job completed \n" + jsonpickle.encode(res_array, unpicklable=False))

@app.task
def task_neo4j_add_order():
    res_array = Neo4jProcessor.sync_order_from_db()
    logger.info("[sync order from db to neo4j] job completed \n" + jsonpickle.encode(res_array, unpicklable=False))
    
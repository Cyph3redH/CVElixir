from app.core.celery_app import app
from app.producers.nvd_producer import publish_nvd
from app.producers.hackernews_producer import publish_hackernews
from app.producers.exploitdb_producer import publish_exploitdb

@app.task
def check_all_sources():
    publish_nvd()
    publish_hackernews()
    publish_exploitdb()
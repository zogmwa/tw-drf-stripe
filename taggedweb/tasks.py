from celery import shared_task

from api import management


@shared_task
def update_sitemap():
    cmd = management.commands.create_sitemap_url.Command()
    opts = {}  # kwargs for sitemap command -- set default url for now...
    cmd.handle(**opts)

from rest_framework.decorators import permission_classes
from django.http import FileResponse

from rest_framework import permissions
from api.management.commands import create_sitemap_url


@permission_classes(permissions.IsAdminUser)
def download_sitemap(request):
    cmd = create_sitemap_url.Command()
    opts = {}  # kwargs for sitemap command -- set default url for now...
    cmd.handle(**opts)

    response = FileResponse(open(u'./static/sitemap.xml', 'rb'))
    response['Content-Disposition'] = 'attachment; filename="%s"' % 'sitemap.xml'
    return response

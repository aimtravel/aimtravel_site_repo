"""Public JSON API root.

Mounted at ``/api/`` (see aimtravel_site/urls.py). The interactive docs and the
OpenAPI schema that drives TypeScript type generation live at:

    /api/docs
    /api/openapi.json

Regenerate the frontend types after changing any schema:

    npm --prefix frontend run generate:api
"""
from ninja import NinjaAPI

from aimtravel_site.api.routers import catalog, home, news, offers, session

# Every endpoint here is an unauthenticated GET, so no auth class is attached.
#
# When write endpoints are added (the tax wizard, staff CRUD), give them
# ``auth=django_auth`` from ``ninja.security``: the SPA is same-origin and
# authenticates with the ordinary Django session cookie, and django_auth is the
# cookie-based backend that also enforces CSRF on unsafe methods. Do not leave
# a write endpoint unauthenticated.
api = NinjaAPI(
    title='AIM Travel API',
    version='1.0.0',
    description='Read API backing the React frontend.',
    urls_namespace='api',
)

api.add_router('/', home.router, tags=['home'])
api.add_router('/', offers.router, tags=['offers'])
api.add_router('/', news.router, tags=['news'])
api.add_router('/', catalog.router, tags=['catalog'])
api.add_router('/', session.router, tags=['session'])

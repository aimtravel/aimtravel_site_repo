"""Current-session identity.

The SPA is served from the same origin as Django, so the existing session
cookie authenticates API calls with no token exchange. This endpoint just tells
the frontend who (if anyone) is signed in, and what they are allowed to see, so
it can render staff controls and the profile menu.
"""
from ninja import Router

from aimtravel_site.api import schemas

router = Router()


@router.get('/auth/me', response=schemas.CurrentUserOut, url_name='me')
def me(request):
    user = request.user
    if not user.is_authenticated:
        return schemas.CurrentUserOut(is_authenticated=False)
    return schemas.CurrentUserOut(
        is_authenticated=True,
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_staff=user.is_staff,
        is_superuser=user.is_superuser,
        picture=schemas.media_url(user.user_picture),
    )

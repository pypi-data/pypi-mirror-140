import logging

from aiohttp import web
from heaserver.service import appproperty, requestproperty
from aiohttp_remotes import XForwardedRelaxed


@web.middleware
async def new_wstl_builder(request: web.Request, handler) -> web.Response:
    wstl_builder_factory = request.app[appproperty.HEA_WSTL_BUILDER_FACTORY]
    request[requestproperty.HEA_WSTL_BUILDER] = wstl_builder_factory()
    response = await handler(request)
    return response


def new_app() -> web.Application:
    """
    Creates and returns an aiohttp Application object. Installs middleware that sets the HEA_WSTL_BUILDER request
    property, assuming that the HEA_WSTL_BUILDER_FACTORY app property has already been set.

    :return: the Application property.
    """
    return web.Application(middlewares=[new_wstl_builder, XForwardedRelaxed().middleware])


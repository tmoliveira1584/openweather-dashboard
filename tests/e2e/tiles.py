"""Tiles do mapa simuladas nos testes de ponta a ponta: o mapa base do CARTO e a camada de
chuva pelo `/api/tiles/precipitation`, sem internet (fatia 11)."""

import re

from playwright.sync_api import Page, Route

from tests.fakes import TRANSPARENT_PNG

CARTO_TILE = re.compile(r"^https://[a-d]\.basemaps\.cartocdn\.com/rastertiles/voyager/")
RAIN_TILE = re.compile(r"/api/tiles/precipitation/")
ZXY = re.compile(r"/(\d+)/(\d+)/(\d+)\.png$")

# Todas as tiles das duas camadas terminaram de carregar.
TILES_DONE_JS = """() => {
    const tiles = [...document.querySelectorAll('#map img.leaflet-tile')];
    return tiles.length > 0 && tiles.every((tile) => tile.complete);
}"""


def zxy(url: str) -> tuple[int, int, int]:
    z, x, y = ZXY.search(url).groups()
    return int(z), int(x), int(y)


class Tiles:
    """Tiles do mapa base (CARTO) e da camada de chuva (`/api/tiles/...`) simuladas.

    - `base` e `rain` guardam o `(z, x, y)` de cada pedido.
    - `base_fails` e `rain_fails` decidem se cada tile falha. A camada de chuva falha como o
      backend: 502 com o código de erro (seção 6.4).
    - Com `hold = True`, os pedidos das duas camadas ficam pendentes em `held`, sem resposta.
    """

    def __init__(self, page: Page):
        self.base: list[tuple[int, int, int]] = []
        self.rain: list[tuple[int, int, int]] = []
        self.base_fails = lambda tile: False
        self.rain_fails = lambda tile: False
        self.hold = False
        self.held: list[Route] = []
        page.route(CARTO_TILE, self._base)
        page.route(RAIN_TILE, self._rain)

    def _base(self, route: Route) -> None:
        tile = zxy(route.request.url)
        self.base.append(tile)
        if self.hold:
            self.held.append(route)
        elif self.base_fails(tile):
            route.abort()
        else:
            route.fulfill(status=200, content_type="image/png", body=TRANSPARENT_PNG)

    def _rain(self, route: Route) -> None:
        tile = zxy(route.request.url)
        self.rain.append(tile)
        if self.hold:
            self.held.append(route)
        elif self.rain_fails(tile):
            route.fulfill(status=502, json={"error": "provider_rate_limited"})
        else:
            route.fulfill(status=200, content_type="image/png", body=TRANSPARENT_PNG)

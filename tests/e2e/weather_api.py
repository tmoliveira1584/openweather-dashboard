"""`/api/weather` simulado no navegador com `page.route`, para os testes de ponta a ponta.

As respostas são o `WeatherView` montado pelo próprio backend a partir das capturas reais
(T-0.8), para que o contrato simulado nunca se afaste do real.
"""

import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import Page, Route

from app.clients.openweather import merge_onecall
from app.domain.view_model import build_weather_view
from app.schemas.provider import OneCallBundle

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
WEATHER_URL = re.compile(r"/api/weather\?")

# Cidades das capturas, no formato `City` do estado (seção 6.5).
UBERLANDIA = {
    "lat": -18.9186,
    "lon": -48.2772,
    "headerLabel": "Uberlândia, BR",
    "markerLabel": "Uberlândia",
    "source": "search",
}
TOKYO = {
    "lat": 35.6895,
    "lon": 139.6917,
    "headerLabel": "Tóquio, JP",
    "markerLabel": "Tóquio",
    "source": "search",
}


def _load(name: str):
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def weather_view(city: str) -> dict:
    """`WeatherView` de "uberlandia" ou "tokyo", como o `/api/weather` devolveria."""
    data = {name: _load(f"onecall4/{city}/{name}.json") for name in ("current", "1min", "1day")}
    pages = [_load(f"onecall4/{city}/1h_p{i}.json") for i in (1, 2)]
    alerts = (
        [_load(f"onecall4/uberlandia/alert_{i}.json") for i in (1, 2, 3)]
        if city == "uberlandia"
        else []
    )
    bundle = merge_onecall(
        current=data["current"],
        minutely=data["1min"],
        hourly_pages=pages,
        daily=data["1day"],
        alerts=alerts,
    )
    return build_weather_view(OneCallBundle.model_validate(bundle)).model_dump(mode="json")


class WeatherApi:
    """`GET /api/weather` simulado no navegador.

    - Cada pedido responde com a próxima resposta de `queue` ou, com a fila vazia, com o
      `WeatherView` da cidade (Tóquio com `lat` 35,…; Uberlândia nos demais casos).
    - Uma resposta é `"ok"`, `"abort"` (o backend não responde) ou `(status, código)`.
    - Com `hold = True`, os pedidos ficam pendentes em `held` até `release(i, resposta)`.
    - `urls` guarda cada pedido recebido, para contar as consultas.
    """

    def __init__(self, page: Page, views: dict[str, dict]):
        self.page = page
        self.views = views
        self.urls: list[str] = []
        self.queue: list = []
        self.held: list[Route] = []
        self.hold = False
        page.route(WEATHER_URL, self._handle)

    def _handle(self, route: Route) -> None:
        self.urls.append(route.request.url)
        if self.hold:
            self.held.append(route)
        else:
            self.reply(route, self.queue.pop(0) if self.queue else "ok")

    def view_for(self, url: str) -> dict:
        lat = parse_qs(urlparse(url).query)["lat"][0]
        return self.views["tokyo" if lat.startswith("35.") else "uberlandia"]

    def reply(self, route: Route, answer="ok") -> None:
        if answer == "abort":
            route.abort()
        elif answer == "ok":
            route.fulfill(json=self.view_for(route.request.url))
        else:
            status, code = answer
            route.fulfill(status=status, json={"error": code})

    def wait_for_held(self, count: int) -> None:
        """Espera até `count` pedidos pendentes: o `fetch` da página chega à rota depois."""
        for _ in range(250):
            if len(self.held) >= count:
                return
            self.page.wait_for_timeout(20)
        raise AssertionError(f"esperava {count} pedidos pendentes, chegaram {len(self.held)}")

    def release(self, index: int = 0, answer="ok") -> None:
        """Responde o pedido pendente de número `index`, esperando-o chegar se preciso."""
        self.wait_for_held(index + 1)
        self.reply(self.held[index], answer)

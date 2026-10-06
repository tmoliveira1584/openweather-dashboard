"""`/api/geo/search` e `/api/geo/reverse` simulados no navegador com `page.route`, para os
testes da busca e da localização.

As respostas são o `CitySearchResult` e o `ReverseResult` montados como o próprio backend faz
(`build_search_result`), a partir da captura real de "Santa Maria" ou de cidades públicas
descritas aqui, para que o contrato simulado nunca se afaste do real.
"""

import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import Page, Route

from app.domain.view_model import build_search_result
from app.schemas.provider import GeoResult

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
SEARCH_URL = re.compile(r"/api/geo/search\?")
REVERSE_URL = re.compile(r"/api/geo/reverse\?")

# Itens no formato da geocodificação direta do provedor (cidades públicas, P-006).
CURITIBA = {
    "name": "Curitiba",
    "local_names": {"pt": "Curitiba"},
    "lat": -25.4295963,
    "lon": -49.2712724,
    "country": "BR",
    "state": "Paraná",
}
CURITIBANOS = {
    "name": "Curitibanos",
    "lat": -27.2829,
    "lon": -50.5816,
    "country": "BR",
    "state": "Santa Catarina",
}
TOKYO = {
    "name": "Tokyo",
    "local_names": {"pt": "Tóquio"},
    "lat": 35.6828387,
    "lon": 139.7594549,
    "country": "JP",
}


def search_result(raw: list[dict]) -> dict:
    """`CitySearchResult` que o `/api/geo/search` devolveria para os itens do provedor."""
    cities = [GeoResult.model_validate(item) for item in raw]
    return build_search_result(cities).model_dump(mode="json")


def reverse_result(raw: list[dict]) -> dict:
    """`ReverseResult` que o `/api/geo/reverse` devolveria: a primeira cidade ou `null`."""
    results = search_result(raw)["results"]
    return {"result": results[0] if results else None}


def _santa_maria() -> list[dict]:
    path = FIXTURES_DIR / "geo_direct_santa_maria.json"
    return json.loads(path.read_text(encoding="utf-8"))


class GeoApi:
    """`GET /api/geo/search` simulado no navegador.

    - `answers` liga o termo recebido (`q`) a uma resposta: a lista de itens do provedor ou
      `(status, código)` para um erro. Termo sem resposta definida: lista vazia.
    - Já vem com "Santa Maria" (captura real, 5 cidades), "Curitiba" (2 cidades) e
      "Tóquio" (1 cidade).
    - Com `hold = True`, os pedidos ficam pendentes em `held` até `release(i)`.
    - `terms` guarda o termo de cada pedido recebido, para contar as buscas.
    - Geocodificação reversa: responde com `reverse_answer` (itens do provedor ou
      `(status, código)`; por padrão, Tóquio) e guarda as coordenadas em `reverse_coords`.
    """

    def __init__(self, page: Page):
        self.page = page
        self.answers: dict[str, object] = {
            "Santa Maria": _santa_maria(),
            "Curitiba": [CURITIBA, CURITIBANOS],
            "Tóquio": [TOKYO],
        }
        self.terms: list[str] = []
        self.held: list[Route] = []
        self.hold = False
        self.reverse_answer: object = [TOKYO]
        self.reverse_coords: list[tuple[str, str]] = []
        page.route(SEARCH_URL, self._handle)
        page.route(REVERSE_URL, self._handle_reverse)

    def _handle_reverse(self, route: Route) -> None:
        query = parse_qs(urlparse(route.request.url).query)
        self.reverse_coords.append((query["lat"][0], query["lon"][0]))
        if isinstance(self.reverse_answer, tuple):
            status, code = self.reverse_answer
            route.fulfill(status=status, json={"error": code})
        else:
            route.fulfill(json=reverse_result(self.reverse_answer))

    def _handle(self, route: Route) -> None:
        self.terms.append(parse_qs(urlparse(route.request.url).query)["q"][0])
        if self.hold:
            self.held.append(route)
        else:
            self.reply(route)

    def reply(self, route: Route) -> None:
        term = parse_qs(urlparse(route.request.url).query)["q"][0]
        answer = self.answers.get(term, [])
        if isinstance(answer, tuple):
            status, code = answer
            route.fulfill(status=status, json={"error": code})
        else:
            route.fulfill(json=search_result(answer))

    def release(self, index: int = 0) -> None:
        """Responde o pedido pendente de número `index`, esperando-o chegar se preciso."""
        for _ in range(250):
            if len(self.held) > index:
                self.reply(self.held[index])
                return
            self.page.wait_for_timeout(20)
        raise AssertionError(f"esperava o pedido {index}, chegaram {len(self.held)}")

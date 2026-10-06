"""Provedor simulado e constantes dos testes. Nenhum teste usa a internet nem a cota."""

import base64

import httpx

FAKE_KEY = "chave-falsa-de-teste"

# PNG transparente de 1x1, no lugar das tiles do CARTO e dos ícones do OpenWeatherMap.
TRANSPARENT_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)
# Momento das capturas da T-0.8: 19:41:05 UTC de 2026-10-05. A 1ª página por hora começa na
# hora cheia (19:00 UTC) e a 2ª, 20 h depois (ADR-013).
CAPTURE_NOW = 1791229265
CAPTURE_HOUR = 1791226800


class FakeProvider:
    """OpenWeatherMap simulado com as capturas reais da T-0.8, para o httpx.MockTransport.

    - Responde pela cidade das coordenadas: Tóquio com `lat` 35,68; Uberlândia nos demais casos.
    - `overrides[endpoint]` troca a resposta de um endpoint por um status HTTP (int), uma
      exceção do httpx (levantada) ou um httpx.Response. Endpoints: current, 1min, 1h_p1,
      1h_p2, 1day, alert, direct, reverse e tile.
    - `with_links=True` põe nas respostas da One Call os links `next`/`prev` com a chave,
      como o provedor real faz (ADR-013).
    - `requests` guarda cada pedido recebido, para conferir URLs e parâmetros.
    """

    def __init__(self, load_json):
        self.load_json = load_json
        self.overrides: dict[str, object] = {}
        self.with_links = False
        self.requests: list[httpx.Request] = []

    def endpoint(self, request: httpx.Request) -> str:
        path = request.url.path
        if request.url.host == "tile.openweathermap.org":
            return "tile"
        if path.startswith("/geo/1.0/"):
            return path.rsplit("/", 1)[1]
        if "/onecall/alert/" in path:
            return "alert"
        name = path.removeprefix("/data/4.0/onecall/").removeprefix("timeline/")
        if name == "1h":
            first_page = int(request.url.params["start"]) == CAPTURE_HOUR
            return "1h_p1" if first_page else "1h_p2"
        return name

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        endpoint = self.endpoint(request)
        override = self.overrides.get(endpoint)
        if isinstance(override, Exception):
            raise override
        if isinstance(override, int):
            return httpx.Response(override, json={"cod": override, "message": "erro simulado"})
        if isinstance(override, httpx.Response):
            # Cópia, para a mesma resposta servir a vários pedidos e testes.
            return httpx.Response(override.status_code, content=override.content)
        return self.respond(endpoint, request)

    def respond(self, endpoint: str, request: httpx.Request) -> httpx.Response:
        params = request.url.params
        if endpoint == "tile":
            return httpx.Response(
                200, content=TRANSPARENT_PNG, headers={"content-type": "image/png"}
            )
        if endpoint == "direct":
            name = "santa_maria" if params["q"] == "Santa Maria" else "empty"
            return httpx.Response(200, json=self.load_json(f"geo_direct_{name}.json"))
        if endpoint == "reverse":
            return httpx.Response(200, json=self.load_json("geo_reverse_uberlandia.json"))
        if endpoint == "alert":
            alert_id = request.url.path.rsplit("/", 1)[1]
            for i in (1, 2, 3):
                detail = self.load_json(f"onecall4/uberlandia/alert_{i}.json")
                if detail["id"] == alert_id:
                    return httpx.Response(200, json=detail)
            return httpx.Response(404, json={"cod": 404})
        city = "tokyo" if params["lat"].startswith("35.") else "uberlandia"
        body = self.load_json(f"onecall4/{city}/{endpoint}.json")
        if self.with_links:
            link = f"https://api.openweathermap.org/data/4.0/onecall/{endpoint}?appid={FAKE_KEY}"
            body.update(next=link, prev=link)
        return httpx.Response(200, json=body)

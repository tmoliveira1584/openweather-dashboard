"""Geolocalização simulada para os testes de ponta a ponta da localização.

O Chrome do Playwright só sabe responder na hora: sem permissão, nega; com permissão, devolve
a coordenada do contexto. Para o usuário que demora a responder (prazo de 10 s, CA-003) e para
a localização tardia (RN-003), a página recebe um `navigator.geolocation` falso, e o teste
decide quando e como ele responde.
"""

from playwright.sync_api import Page

_FAKE = """
(() => {
  const calls = [];
  const fake = {
    getCurrentPosition(success, error, options) {
      calls.push({ success, error, options });
    },
    watchPosition() {
      throw new Error('watchPosition não é usado');
    },
    clearWatch() {},
  };
  Object.defineProperty(Navigator.prototype, 'geolocation', {
    configurable: true,
    get: () => fake,
  });
  window.__fakeGeolocation = {
    calls: () => calls.map((call) => call.options ?? null),
    succeed(lat, lon) {
      const position = { coords: { latitude: lat, longitude: lon, accuracy: 20 },
                         timestamp: Date.now() };
      for (const call of calls) call.success(position);
    },
    deny() {
      const error = { code: 1, message: 'User denied Geolocation', PERMISSION_DENIED: 1 };
      for (const call of calls) call.error?.(error);
    },
  };
})();
"""

_ABSENT = "delete Navigator.prototype.geolocation;"


class FakeGeolocation:
    """`navigator.geolocation` falso: os pedidos ficam pendentes até `succeed` ou `deny`.

    Instale antes de abrir a página (`page.add_init_script`).
    """

    def __init__(self, page: Page):
        self.page = page
        page.add_init_script(_FAKE)

    def calls(self) -> list[dict | None]:
        """Opções de cada `getCurrentPosition` recebido, na ordem."""
        return self.page.evaluate("() => window.__fakeGeolocation.calls()")

    def succeed(self, lat: float, lon: float) -> None:
        """O navegador informa a coordenada (dentro ou fora do prazo)."""
        self.page.evaluate("([lat, lon]) => window.__fakeGeolocation.succeed(lat, lon)", [lat, lon])

    def deny(self) -> None:
        """O usuário nega a permissão."""
        self.page.evaluate("() => window.__fakeGeolocation.deny()")


def remove_geolocation(page: Page) -> None:
    """Navegador sem o recurso de localização. Instale antes de abrir a página."""
    page.add_init_script(_ABSENT)


def allow_location(page: Page, lat: float, lon: float) -> None:
    """O usuário autoriza a localização, e o Chrome informa a coordenada na hora."""
    page.context.grant_permissions(["geolocation"])
    page.context.set_geolocation({"latitude": lat, "longitude": lon})

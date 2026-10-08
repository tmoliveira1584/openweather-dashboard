"""Fusos exóticos (plano de testes, fase 3, TS-3.1 e TS-3.2): a mesma captura de Uberlândia
com o fuso trocado para um extremo (+14:00, Kiribati) e para um fuso com 45 minutos (+05:45,
Nepal). As previsões do provedor seguem em horas cheias de UTC, que nesses fusos não caem em
horas cheias locais, e o dia da cidade já é terça enquanto em UTC ainda é segunda.

O relógio começa parado às 19:42:05 UTC de segunda, 05/10/2026 (`open_paused`).
"""

import copy
import re

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.clock import open_paused
from tests.e2e.weather_api import bundle, view_of

KIRIBATI = 14 * 3600
NEPAL = 5 * 3600 + 45 * 60


def view_with_offset(offset: int) -> dict:
    """`WeatherView` da captura de Uberlândia como se a cidade estivesse no fuso `offset`."""
    raw = copy.deepcopy(bundle("uberlandia"))
    raw["timezone_offset"] = offset
    return view_of(raw)


@pytest.mark.parametrize(
    ("offset", "now", "agora", "hours"),
    [
        (KIRIBATI, "09:41", "09:42", ["09:00", "10:00", "11:00"]),
        (NEPAL, "01:26", "01:27", ["00:45", "01:45", "02:45"]),
    ],
    ids=["kiribati_+14", "nepal_+05_45"],
)
def test_p_015_exotic_timezone_shows_the_city_local_time_in_every_block(
    page: Page, weather_api, offset, now, agora, hours
):
    """P-015, RN-015, RN-026, RN-034, RN-035, RN-043: num fuso extremo ou com 45 minutos,
    todos os blocos usam a hora local da cidade. "Hoje" já é terça (em UTC ainda é segunda),
    e cada hora da previsão traz o horário local em que ela começa."""
    weather_api.queue = [view_with_offset(offset)]
    open_paused(page)
    expect(page.locator(".current")).to_have_attribute("data-block-state", "ready")

    expect(page.locator(".current-time")).to_have_text(now)
    expect(page.locator(".day-tab-label").nth(0)).to_have_text("Hoje")
    expect(page.locator(".day-tab-label").nth(1)).to_have_text("Qua")
    labels = page.locator(".hour-label")
    for index, hour in enumerate(hours):
        expect(labels.nth(index)).to_have_text(re.compile(f"^{hour}"))
    expect(page.locator(".mark-time").first).to_have_text(agora)

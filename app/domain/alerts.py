"""Selo de alertas e alertas por dia (RN-018, RN-032)."""

from datetime import UTC, datetime

from app.schemas.provider import Alert

MAX_SHOWN = 99  # acima disso, "99+ alertas" (RN-018)
DAY_SECONDS = 86_400


def alerts_label(count: int) -> str | None:
    """Selo "1 alerta", "N alertas" ou "99+ alertas"; `None` sem alertas, e o selo some (RN-018)."""
    if count <= 0:
        return None
    if count == 1:
        return "1 alerta"
    if count > MAX_SHOWN:
        return f"{MAX_SHOWN}+ alertas"
    return f"{count} alertas"


def count_alert_ids(ids: list[str] | None) -> int:
    """Número de IDs distintos e não vazios, inclusive de alertas futuros (RN-018).

    A falta da lista equivale a 0. Usado no selo de "Hoje", com `current.alerts`.
    """
    return len({alert_id for alert_id in ids or [] if alert_id and alert_id.strip()})


def _day_period(local_date: str, offset: int) -> tuple[int, int]:
    """Início e fim (UTC) do período de 00:00 a 24:00 de `local_date` no fuso da cidade."""
    midnight = datetime.fromisoformat(local_date).replace(tzinfo=UTC)
    start = int(midnight.timestamp()) - offset
    return start, start + DAY_SECONDS


def count_alerts_on_day(alerts: list[Alert], local_date: str, offset: int) -> int:
    """Alertas cuja vigência se sobrepõe ao dia por um tempo maior que zero (RN-032).

    Um alerta sem início ou sem fim conta em todos os dias. Um alerta que termina às 00:00
    conta só no dia anterior. `local_date` é "AAAA-MM-DD" e `offset`, o fuso da cidade em
    segundos. O pacote traz um alerta por ID distinto (seção 6.2 da arquitetura).
    """
    day_start, day_end = _day_period(local_date, offset)
    return sum(
        1
        for alert in alerts
        if alert.start is None
        or alert.end is None
        or min(alert.end, day_end) - max(alert.start, day_start) > 0
    )

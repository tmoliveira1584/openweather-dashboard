"""Hora local da cidade e rótulos de hora, dia e data (RN-015, RN-028, RN-030, RN-035).

Hora local = `dt` (UTC) + `offset` do provedor, lida como UTC. Nunca usa o fuso da máquina
(seção 7.5 da arquitetura, P-015). `ts` é o `dt` em segundos e `offset`, o fuso em segundos.
"""

from datetime import UTC, datetime

WEEKDAYS = ("Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom")  # ordem do datetime.weekday()


def local_datetime(ts: int, offset: int) -> datetime:
    """Data e hora locais da cidade, num datetime em UTC deslocado pelo fuso (RN-015)."""
    return datetime.fromtimestamp(ts + offset, tz=UTC)


def time_label(ts: int, offset: int) -> str:
    """Hora local "HH:MM" em 24 horas, como "08:18" (RN-015)."""
    moment = local_datetime(ts, offset)
    return f"{moment.hour:02d}:{moment.minute:02d}"


def hour_label(ts: int, offset: int) -> str:
    """Hora local "HH:00" da previsão hora a hora, como "13:00" (RN-035)."""
    return f"{local_datetime(ts, offset).hour:02d}:00"


def weekday_label(ts: int, offset: int) -> str:
    """Dia da semana abreviado em português: Dom, Seg, …, Sáb (RN-028)."""
    return WEEKDAYS[local_datetime(ts, offset).weekday()]


def date_label(ts: int, offset: int) -> str:
    """Data no formato "Seg, 05/10" (RN-030)."""
    moment = local_datetime(ts, offset)
    return f"{WEEKDAYS[moment.weekday()]}, {moment.day:02d}/{moment.month:02d}"


def local_date(ts: int, offset: int) -> str:
    """Data local "AAAA-MM-DD", usada para achar "Hoje" (RN-026)."""
    return local_datetime(ts, offset).date().isoformat()

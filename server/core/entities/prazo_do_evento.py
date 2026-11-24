"""Calendar rules for events: today in Brasília and the end of the period.

Dates are stored in UTC (D-023), but an event happens on a calendar day of
the campus, so "today" and "the day after" follow Brasília time (D-009).
"""

from datetime import date, datetime, time, timedelta, timezone

# Brazil has had no daylight saving time since 2019, so Brasília is a fixed
# UTC-3. This avoids depending on a time zone database, which Windows lacks.
FUSO_DA_PUC = timezone(timedelta(hours=-3), "BRT")


def dia_de_hoje(agora: datetime) -> date:
    """Return the calendar day, in Brasília, of the instant `agora`."""
    if agora.tzinfo is None:
        agora = agora.replace(tzinfo=timezone.utc)
    return agora.astimezone(FUSO_DA_PUC).date()


def fim_do_prazo_do_evento(data_evento: date) -> datetime:
    """Return, in UTC, the start of the day after the event (Brasília)."""
    dia_seguinte = data_evento + timedelta(days=1)
    inicio = datetime.combine(dia_seguinte, time.min, tzinfo=FUSO_DA_PUC)
    return inicio.astimezone(timezone.utc)

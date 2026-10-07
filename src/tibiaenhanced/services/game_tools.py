"""Regras locais de EXP Share e agenda do Rashid pelo server save."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def exp_share_range(level: int) -> tuple[int, int]:
    """Invert floor(2 * highest / 3) <= lowest using integer arithmetic."""
    if type(level) is not int or level < 1:
        raise ValueError("Informe um level inteiro maior que zero.")
    return max(1, 2 * level // 3), (3 * level + 2) // 2


@dataclass(frozen=True)
class RashidStop:
    weekday: str
    city: str
    directions: str
    position: tuple[int, int, int]

    @property
    def map_url(self) -> str:
        x, y, z = self.position
        return f"https://tibiamaps.io/map#{x},{y},{z}:2"


RASHID_WEEK = (
    RashidStop("Segunda-feira", "Svargrond", "Taverna de Dankwart, ao sul do templo.", (32210, 31158, 7)),
    RashidStop("Terça-feira", "Liberty Bay", "Taverna de Lyonel, a oeste do depot.", (32301, 32837, 7)),
    RashidStop("Quarta-feira", "Port Hope", "Taverna de Clyde, ao norte do barco.", (32578, 32754, 7)),
    RashidStop("Quinta-feira", "Ankrahmun", "Taverna de Arito, acima do post office.", (33070, 32882, 6)),
    RashidStop("Sexta-feira", "Darashia", "Taverna de Miraia, a oeste do barco.", (33235, 32485, 7)),
    RashidStop("Sábado", "Edron", "Taverna de Mirabell, acima do depot.", (33168, 31809, 6)),
    RashidStop("Domingo", "Carlin", "Primeiro andar do depot.", (32330, 31782, 6)),
)


def rashid_today(now: datetime | None = None) -> tuple[RashidStop, datetime]:
    """The Tibia day starts at 10:00 Europe/Berlin, including summer time."""
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("O horário precisa incluir o fuso.")
    berlin = now.astimezone(ZoneInfo("Europe/Berlin"))
    save = berlin.replace(hour=10, minute=0, second=0, microsecond=0)
    if berlin < save:
        game_date = berlin.date() - timedelta(days=1)
        next_save = save
    else:
        game_date = berlin.date()
        next_save = save + timedelta(days=1)
    return RASHID_WEEK[game_date.weekday()], next_save

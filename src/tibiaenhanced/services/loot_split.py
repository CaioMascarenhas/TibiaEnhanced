"""Leitura do Party Hunt Analyzer e acerto de saldos em gp inteiros."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import html
import re


@dataclass(frozen=True)
class PlayerLoot:
    name: str
    loot: int
    supplies: int
    damage: int | None = None
    healing: int | None = None

    @property
    def balance(self) -> int:
        return self.loot - self.supplies


@dataclass(frozen=True)
class HuntSession:
    players: tuple[PlayerLoot, ...]
    duration_minutes: int | None
    duration_text: str
    loot_type: str

    @property
    def balance(self) -> int:
        return sum(player.balance for player in self.players)


@dataclass(frozen=True)
class Transfer:
    sender: str
    recipient: str
    amount: int

    @property
    def command(self) -> str:
        return f"transfer {self.amount} to {self.recipient}"


@dataclass(frozen=True)
class SplitResult:
    session: HuntSession
    shares: tuple[int, ...]
    transfers: tuple[Transfer, ...]

    @property
    def share(self) -> Decimal:
        return Decimal(self.session.balance) / len(self.session.players)

    @property
    def share_per_hour(self) -> Decimal | None:
        minutes = self.session.duration_minutes
        return self.share * 60 / minutes if minutes else None


_METRIC = re.compile(r"^(Loot|Supplies|Balance|Damage|Healing)\s*:\s*(.*?)\s*$", re.I)
_NUMBER = re.compile(r"^[+-]?(?:\d+|\d{1,3}(?:,\d{3})+|\d{1,3}(?:\.\d{3})+)$")


def _number(value: str, field: str) -> int:
    if not _NUMBER.fullmatch(value):
        raise ValueError(f"Valor inválido em {field}: {value!r}. Use valores inteiros do log.")
    number = int(value.replace(",", "").replace(".", ""))
    if field != "balance" and number < 0:
        raise ValueError(f"{field.title()} não pode ser negativo.")
    return number


def parse_session(text: str) -> HuntSession:
    if len(text) > 1_000_000:
        raise ValueError("O log é muito grande. Cole apenas uma sessão do Party Hunt Analyzer.")
    text = html.unescape(text).replace("\xa0", " ").replace("\\n", "\n").replace("\\", "\n")
    players = []
    seen_names = set()
    totals = {}
    name = None
    fields = {}
    duration_minutes = None
    duration_text = "Não informada"
    loot_type = "Não informado"

    def finish_player() -> None:
        if name is None:
            return
        missing = {"loot", "supplies", "balance"} - fields.keys()
        if missing:
            raise ValueError(f"Log incompleto para {name}: falta {', '.join(sorted(missing))}.")
        if name.casefold() in seen_names:
            raise ValueError(f"Jogador repetido no log: {name}. Cole apenas uma sessão.")
        if fields["balance"] != fields["loot"] - fields["supplies"]:
            raise ValueError(f"Saldo inconsistente para {name}: Loot menos Supplies difere de Balance.")
        seen_names.add(name.casefold())
        players.append(PlayerLoot(name, fields["loot"], fields["supplies"],
                                  fields.get("damage"), fields.get("healing")))

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lower = line.lower()
        if lower.startswith("session data:"):
            continue
        if lower.startswith("session:"):
            match = re.fullmatch(r"Session:\s*(\d+):(\d{2})h?", line, re.I)
            if not match or not 0 <= int(match[2]) < 60:
                raise ValueError("Duração inválida. Esperado Session: HH:MMh.")
            if duration_minutes is not None:
                raise ValueError("Mais de uma sessão no log. Cole apenas uma sessão.")
            duration_minutes = int(match[1]) * 60 + int(match[2])
            duration_text = f"{int(match[1]):02}:{int(match[2]):02}h"
            continue
        if lower.startswith("loot type:"):
            loot_type = line.split(":", 1)[1].strip()
            continue
        metric = _METRIC.fullmatch(line)
        if metric:
            field = metric[1].lower()
            target = totals if name is None else fields
            if field in target:
                raise ValueError(f"Campo {field.title()} repetido. Cole apenas uma sessão completa.")
            target[field] = _number(metric[2], field)
            continue
        if ":" in line or len(line) > 64:
            raise ValueError(f"Linha não reconhecida: {line[:80]}. Cole o log original do Analyzer.")
        finish_player()
        name = re.sub(r"\s*\(Leader\)\s*$", "", line, flags=re.I).strip()
        if not name:
            raise ValueError("Nome de jogador vazio no log.")
        fields = {}
    finish_player()
    if not players:
        raise ValueError("Nenhum jogador encontrado. Cole o log completo do Party Hunt Analyzer.")
    for field in ("loot", "supplies", "balance", "damage", "healing"):
        if field in totals:
            values = [getattr(player, field) for player in players]
            if any(value is None for value in values) or sum(values) != totals[field]:
                raise ValueError(f"O total de {field.title()} não confere com os jogadores. Verifique se o log está completo.")
    return HuntSession(tuple(players), duration_minutes, duration_text, loot_type)


def split_loot(session: HuntSession) -> SplitResult:
    if not session.players:
        raise ValueError("A sessão precisa ter ao menos um jogador.")
    base, remainder = divmod(session.balance, len(session.players))
    shares = tuple(base + (index < remainder) for index in range(len(session.players)))
    payers, receivers = [], []
    for player, share in zip(session.players, shares):
        delta = player.balance - share
        if delta > 0:
            payers.append([player.name, delta])
        elif delta < 0:
            receivers.append([player.name, -delta])
    # Largest balances first keeps settlements short and deterministic.
    payers.sort(key=lambda item: -item[1])
    receivers.sort(key=lambda item: -item[1])
    transfers = []
    receiver_index = 0
    for sender, amount in payers:
        while amount:
            recipient, needed = receivers[receiver_index]
            paid = min(amount, needed)
            transfers.append(Transfer(sender, recipient, paid))
            amount -= paid
            receivers[receiver_index][1] -= paid
            if receivers[receiver_index][1] == 0:
                receiver_index += 1
    return SplitResult(session, shares, tuple(transfers))


def compact_gold(value: int | Decimal) -> str:
    value = Decimal(value)
    if abs(value) >= 1_000_000:
        scaled = (value / 1_000_000).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{scaled.normalize():f}kk"
    if abs(value) >= 1_000:
        return f"{(value / 1_000).quantize(Decimal('1'), rounding=ROUND_HALF_UP):f}k"
    return f"{value.quantize(Decimal('1'), rounding=ROUND_HALF_UP):f}"


def damage_split(session: HuntSession) -> tuple[tuple[str, Decimal], ...]:
    if any(player.damage is None for player in session.players):
        return ()
    total = sum(player.damage for player in session.players)
    if not total:
        return ()
    return tuple((player.name, (Decimal(player.damage) * 100 / total).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP))
        for player in sorted(session.players, key=lambda player: -player.damage))

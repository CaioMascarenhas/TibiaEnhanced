"""Acertos exatos, limites inteiros de share e virada diária do server save."""

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import random
import unittest
from zoneinfo import ZoneInfo

from tibiaenhanced.services.game_tools import exp_share_range, rashid_today
from tibiaenhanced.services.loot_split import (
    HuntSession, PlayerLoot, compact_gold, damage_split, parse_session, split_loot,
)


SAMPLE = (Path(__file__).parent / "fixtures" / "party_hunt.txt").read_text(encoding="utf-8")


class LootSplitTests(unittest.TestCase):
    def test_user_example_matches_exact_bank_commands_and_damage(self):
        result = split_loot(parse_session(SAMPLE))
        self.assertEqual(result.session.balance, 1_835_265)
        self.assertEqual(result.shares, (611_755,) * 3)
        self.assertEqual([transfer.command for transfer in result.transfers],
                         ["transfer 327375 to Kandin", "transfer 139014 to Kandin"])
        self.assertEqual(compact_gold(result.session.balance), "1.84kk")
        self.assertEqual(compact_gold(result.share), "612k")
        self.assertEqual(compact_gold(result.share_per_hour), "693k")
        self.assertEqual(damage_split(result.session), (
            ("Kandin", Decimal("43.6")), ("Blackfang", Decimal("36.4")),
            ("Albus Cruciatus", Decimal("20.0"))))

    def test_accepts_html_spaces_crlf_and_literal_line_separators(self):
        session = parse_session(SAMPLE.replace("    ", "&#x20;   ").replace("\n", "\\\r\n"))
        self.assertEqual(session, parse_session(SAMPLE))
        self.assertEqual(parse_session(SAMPLE.replace("\n", "\\n")), session)
        self.assertEqual(parse_session(SAMPLE.replace(",", ".").split("\n", 1)[1]), session)

    def test_random_parties_conserve_money_and_equalize_positive_and_negative_balances(self):
        rng = random.Random(274)
        for count in (1, 2, 3, 4, 7, 20, 60):
            for _ in range(25):
                players = tuple(PlayerLoot(f"Player {i}", rng.randrange(5000), rng.randrange(9000))
                                for i in range(count))
                session = HuntSession(players, 60, "01:00h", "Market")
                result = split_loot(session)
                balances = {player.name: player.balance for player in players}
                for transfer in result.transfers:
                    self.assertGreater(transfer.amount, 0)
                    self.assertNotEqual(transfer.sender, transfer.recipient)
                    balances[transfer.sender] -= transfer.amount
                    balances[transfer.recipient] += transfer.amount
                self.assertEqual(tuple(balances.values()), result.shares)
                self.assertEqual(sum(balances.values()), session.balance)
                self.assertLessEqual(max(balances.values()) - min(balances.values()), 1)
                self.assertLessEqual(len(result.transfers), count - 1)

    def test_rejects_incomplete_inconsistent_duplicate_and_invalid_logs(self):
        invalid = (
            "", SAMPLE.replace("Supplies: 497,256", "Supplies: x"),
            SAMPLE.replace("Balance: 939,130", "Balance: 939,131"),
            SAMPLE.replace("Loot: 2,838,314", "Loot: 2,838,315"),
            SAMPLE.replace("    Supplies: 497,256\n", ""),
            SAMPLE.replace("Blackfang", "Albus Cruciatus"),
            SAMPLE.replace("Session: 00:53h", "Session: 00:99h"),
            SAMPLE + SAMPLE, SAMPLE.replace("Loot: 642,622", "Loot: -642,622"),
        )
        for text in invalid:
            with self.subTest(text=text[:80]), self.assertRaises(ValueError):
                parse_session(text)

    def test_zero_damage_no_duration_and_single_player(self):
        session = parse_session("Solo\nLoot: 0\nSupplies: 10\nBalance: -10\nDamage: 0")
        result = split_loot(session)
        self.assertEqual(result.shares, (-10,))
        self.assertEqual(result.transfers, ())
        self.assertIsNone(result.share_per_hour)
        self.assertEqual(damage_split(session), ())
        self.assertIsNone(split_loot(parse_session("Session: 00:00h\nSolo\nLoot: 0\nSupplies: 0\nBalance: 0")).share_per_hour)


class ExpShareTests(unittest.TestCase):
    def test_ranges_are_symmetric_and_include_exact_integer_boundaries(self):
        self.assertEqual(exp_share_range(200), (133, 301))
        self.assertEqual(exp_share_range(100), (66, 151))
        self.assertEqual(exp_share_range(1), (1, 2))
        for level in range(1, 1000):
            low, high = exp_share_range(level)
            for partner in (low, high):
                partner_low, partner_high = exp_share_range(partner)
                self.assertLessEqual(partner_low, level)
                self.assertGreaterEqual(partner_high, level)
            self.assertLessEqual(2 * high // 3, level)
            self.assertGreater(2 * (high + 1) // 3, level)
        for value in (0, -1, 1.5, True):
            with self.assertRaises(ValueError):
                exp_share_range(value)


class RashidTests(unittest.TestCase):
    def test_before_and_after_save_in_fortaleza_summer_and_winter(self):
        zone = ZoneInfo("America/Fortaleza")
        for month, hour in ((10, 5), (1, 6)):
            # Both dates are Wednesdays in 2026.
            day = 7
            before, save = rashid_today(datetime(2026, month, day, hour - 1, 59, tzinfo=zone))
            after, _ = rashid_today(datetime(2026, month, day, hour, 0, tzinfo=zone))
            self.assertEqual(before.city, "Liberty Bay")
            self.assertEqual(after.city, "Port Hope")
            self.assertEqual(after.map_url, "https://tibiamaps.io/map#32578,32754,7:2")
            self.assertEqual(save.astimezone(zone).hour, hour)

    def test_week_schedule_and_european_dst_transitions(self):
        berlin = ZoneInfo("Europe/Berlin")
        expected = ("Svargrond", "Liberty Bay", "Port Hope", "Ankrahmun", "Darashia", "Edron", "Carlin")
        for day, city in enumerate(expected, start=5):
            stop, _ = rashid_today(datetime(2026, 10, day, 12, tzinfo=berlin))
            self.assertEqual(stop.city, city)
        for month, day, expected_utc_hour in ((3, 29, 8), (10, 25, 9)):
            _, next_save = rashid_today(datetime(2026, month, day, 9, tzinfo=berlin))
            self.assertEqual(next_save.astimezone(timezone.utc).hour, expected_utc_hour)
        with self.assertRaises(ValueError):
            rashid_today(datetime(2026, 10, 7))


if __name__ == "__main__":
    unittest.main()

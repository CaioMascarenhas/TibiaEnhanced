"""Perfis locais versionados, gravados de forma atômica."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QStandardPaths


SCHEMA_VERSION = 1
DEFAULT_PROFILE = "Padrão"


def empty_profile() -> dict:
    return {"audio": {}, "recortes": []}


class ProfileStore:
    def __init__(self, path: Path | None = None) -> None:
        if path is None:
            folder = Path(QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppConfigLocation))
            path = folder / "profiles.json"
        self.path = path
        self._save_blocked = False
        self.data = {
            "schema_version": SCHEMA_VERSION,
            "active_profile": DEFAULT_PROFILE,
            "profiles": {DEFAULT_PROFILE: empty_profile()},
        }

    def load(self) -> list[str]:
        if not self.path.is_file():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict) or raw.get("schema_version") != SCHEMA_VERSION:
                raise ValueError("versão de esquema desconhecida")
            profiles = raw.get("profiles")
            if not isinstance(profiles, dict) or not profiles:
                raise ValueError("lista de perfis inválida")
            valid = {
                name: profile for name, profile in profiles.items()
                if isinstance(name, str) and name.strip() and isinstance(profile, dict)
            }
            if not valid:
                raise ValueError("nenhum perfil válido")
            active = raw.get("active_profile")
            if not isinstance(active, str) or active not in valid:
                active = next(iter(valid))
            self.data = {
                "schema_version": SCHEMA_VERSION,
                "active_profile": active,
                "profiles": valid,
            }
            return (["Alguns perfis inválidos foram ignorados."]
                    if len(valid) != len(profiles) else [])
        except (OSError, ValueError, TypeError) as exc:
            backup = self.path.with_name(
                f"profiles-invalid-{datetime.now():%Y%m%d-%H%M%S-%f}.json")
            try:
                shutil.copy2(self.path, backup)
                return [f"Configuração inválida ({exc}). Cópia preservada em {backup}."]
            except OSError:
                self._save_blocked = True
                return [f"Configuração inválida ({exc}). Não foi possível criar uma cópia; gravação desativada para preservar o arquivo original."]

    @property
    def active_name(self) -> str:
        return self.data["active_profile"]

    @property
    def active(self) -> dict:
        return self.data["profiles"][self.active_name]

    def create(self, name: str) -> None:
        name = name.strip()
        if not name or len(name) > 80:
            raise ValueError("Informe um nome de até 80 caracteres.")
        if any(existing.casefold() == name.casefold() for existing in self.data["profiles"]):
            raise ValueError("Já existe um perfil com esse nome.")
        previous = self.active_name
        self.data["profiles"][name] = empty_profile()
        self.data["active_profile"] = name
        try:
            self.save()
        except OSError:
            del self.data["profiles"][name]
            self.data["active_profile"] = previous
            raise

    def select(self, name: str) -> None:
        if name not in self.data["profiles"]:
            raise ValueError("Perfil não encontrado")
        previous = self.active_name
        self.data["active_profile"] = name
        try:
            self.save()
        except OSError:
            self.data["active_profile"] = previous
            raise

    def save(self) -> None:
        if self._save_blocked:
            raise OSError("o arquivo inválido não pôde ser copiado; gravação desativada")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self.data, ensure_ascii=False, indent=2)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent,
                                             prefix=".profiles-", suffix=".tmp",
                                             delete=False) as file:
                temporary = Path(file.name)
                file.write(payload)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()

"""Ferramentas locais de hunt, experiência compartilhada e agenda do Rashid."""

from PySide6.QtCore import QPoint, QSize, QTimer, Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QKeySequence, QMovie, QShortcut
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLayout, QLineEdit, QPlainTextEdit, QPushButton, QScrollArea, QSpinBox,
    QSizePolicy, QVBoxLayout, QWidget,
)

from ..services.game_tools import exp_share_range, rashid_today
from ..services.loot_split import compact_gold, damage_split, parse_session, split_loot
from .design import ASSETS


def _label(text: str, name: str = "", *, wrap: bool = False) -> QLabel:
    label = QLabel(text)
    label.setTextFormat(Qt.TextFormat.PlainText)
    label.setObjectName(name)
    label.setWordWrap(wrap)
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    return label


def _copy_button(caption: str, value: str) -> QPushButton:
    button = QPushButton(caption)
    button.setAccessibleName(caption)
    reset = QTimer(button)
    reset.setSingleShot(True)
    reset.setInterval(1600)
    reset.timeout.connect(lambda: button.setText(caption))

    def copy() -> None:
        QApplication.clipboard().setText(value)
        button.setText("Copiado!")
        reset.start()

    button.clicked.connect(copy)
    return button


class _ToolStack(QWidget):
    """Only the selected tool determines the scrollable content's height."""

    currentChanged = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self._pages = []
        self._index = 0
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)

    def addWidget(self, page) -> None:
        self.layout().addWidget(page)
        self._pages.append(page)
        page.setVisible(len(self._pages) == 1)

    def currentWidget(self):
        return self._pages[self._index]

    def setCurrentIndex(self, index: int) -> None:
        if index == self._index:
            return
        self.currentWidget().hide()
        self._index = index
        self.currentWidget().show()
        self.updateGeometry()
        self.currentChanged.emit(index)


class LootSplitPanel(QWidget):
    calculated = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.result = None
        self.transfer_copy_buttons = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(_label("Cole a sessão do Party Hunt Analyzer para dividir supplies e lucro igualmente.",
                                "pageDescription", wrap=True))
        self.log_input = QPlainTextEdit()
        self.log_input.setObjectName("huntLog")
        self.log_input.setAccessibleName("Log do Party Hunt Analyzer")
        self.log_input.setPlaceholderText(
            "Session data: From ... to ...\nSession: 00:53h\nLoot Type: Market\nLoot: ...\n"
            "Supplies: ...\nBalance: ...\nNome do jogador\n    Loot: ...\n    Supplies: ...\n    Balance: ...")
        self.log_input.setFixedHeight(150)
        layout.addWidget(self.log_input)
        actions = QHBoxLayout()
        self.calculate_button = QPushButton("Dividir loot")
        self.calculate_button.setObjectName("primaryButton")
        self.calculate_button.clicked.connect(self.calculate)
        actions.addWidget(self.calculate_button)
        paste = QPushButton("Colar")
        paste.clicked.connect(lambda: self.log_input.setPlainText(QApplication.clipboard().text()))
        actions.addWidget(paste)
        clear = QPushButton("Limpar")
        clear.clicked.connect(self.log_input.clear)
        actions.addWidget(clear)
        actions.addStretch()
        layout.addLayout(actions)
        self.error_label = _label("", "toolError", wrap=True)
        self.error_label.hide()
        layout.addWidget(self.error_label)
        self.results = QWidget()
        self.result_layout = QVBoxLayout(self.results)
        self.result_layout.setContentsMargins(0, 0, 0, 0)
        self.result_layout.setSpacing(12)
        layout.addWidget(self.results)
        self.results.hide()
        self.log_input.textChanged.connect(self._invalidate)
        self.calculate_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.calculate_shortcut.activated.connect(self.calculate)

    def _invalidate(self) -> None:
        self.result = None
        self.results.hide()
        self.error_label.hide()

    def _clear_results(self) -> None:
        self.transfer_copy_buttons = []
        while self.result_layout.count():
            item = self.result_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.deleteLater()

    def calculate(self) -> None:
        self._invalidate()
        self._clear_results()
        try:
            self.result = split_loot(parse_session(self.log_input.toPlainText()))
        except ValueError as exc:
            self.error_label.setText(str(exc))
            self.error_label.show()
            return
        self._render_result()
        self.results.show()
        self.calculated.emit()

    def _render_result(self) -> None:
        result = self.result
        session = result.session
        summary = QFrame()
        summary.setObjectName("card")
        stats = QGridLayout(summary)
        stats.setContentsMargins(16, 14, 16, 14)
        stats.setHorizontalSpacing(18)
        per_hour = result.share_per_hour
        for column, (caption, value, exact) in enumerate((
            ("Lucro total" if session.balance >= 0 else "Prejuízo total", compact_gold(session.balance),
             f"{session.balance:,} gp"),
            ("Por jogador", compact_gold(result.share), f"{result.share:,.2f} gp"),
            ("Por jogador / hora", compact_gold(per_hour) if per_hour is not None else "—",
             f"{per_hour:,.2f} gp/h" if per_hour is not None else "Duração não informada ou zero"),
        )):
            stats.addWidget(_label(caption, "mutedText"), 0, column)
            number = _label(value, "toolNumber")
            number.setToolTip(exact)
            stats.addWidget(number, 1, column)
            stats.setColumnStretch(column, 1)
        self.result_layout.addWidget(summary)
        self.result_layout.addWidget(_label(
            f"{len(session.players)} jogador(es) · Sessão: {session.duration_text} · Loot: {session.loot_type}",
            "mutedText", wrap=True))
        remainder = session.balance % len(session.players)
        if remainder:
            self.result_layout.addWidget(_label(
                "A sobra foi distribuída na ordem do log. A diferença final é de no máximo 1 gp por jogador.",
                "mutedText", wrap=True))
        self.result_layout.addWidget(_label("Transferências", "sectionTitle"))
        if not result.transfers:
            self.result_layout.addWidget(_label("Os saldos já estão divididos. Nenhuma transferência necessária.",
                                               "mutedText", wrap=True))
        for transfer in result.transfers:
            card = QFrame()
            card.setObjectName("card")
            box = QVBoxLayout(card)
            box.setContentsMargins(14, 12, 14, 12)
            box.setSpacing(8)
            box.addWidget(_label(f"{transfer.sender} → {transfer.recipient} · {compact_gold(transfer.amount)} gp",
                                 "transferTitle", wrap=True))
            row = QHBoxLayout()
            command = QLineEdit(transfer.command)
            command.setReadOnly(True)
            command.setAccessibleName(f"Comando de {transfer.sender} para {transfer.recipient}")
            command.setToolTip(f"Valor exato: {transfer.amount:,} gp")
            row.addWidget(command, 1)
            copy = _copy_button("Copiar comando", transfer.command)
            self.transfer_copy_buttons.append(copy)
            row.addWidget(copy)
            box.addLayout(row)
            self.result_layout.addWidget(card)
        split = damage_split(session)
        if split:
            text = " · ".join(f"{name}: {percentage.normalize():f}%" for name, percentage in split)
            self.result_layout.addWidget(_label("Damage Split", "sectionTitle"))
            self.result_layout.addWidget(_label(text, "mutedText", wrap=True))
        self.result_layout.addWidget(_label("Saldo após o acerto", "sectionTitle"))
        for player, share in zip(session.players, result.shares):
            self.result_layout.addWidget(_label(f"{player.name}: {share:,} gp", "mutedText", wrap=True))
        self.copy_result_button = _copy_button("Copiar resultado", self.result_text())
        self.result_layout.addWidget(self.copy_result_button, alignment=Qt.AlignmentFlag.AlignLeft)

    def result_text(self) -> str:
        if self.result is None:
            return ""
        result = self.result
        lines = [f"Loot Split · {len(result.session.players)} jogadores · {result.session.duration_text}"]
        for transfer in result.transfers:
            lines.append(f"{transfer.sender} paga {transfer.amount:,} gp para {transfer.recipient} "
                         f"(Bank: {transfer.command})")
        if not result.transfers:
            lines.append("Nenhuma transferência necessária.")
        lines.extend((f"Saldo total: {result.session.balance:,} gp (~{compact_gold(result.session.balance)}).",
                      f"Por jogador: ~{compact_gold(result.share)} gp."))
        if result.share_per_hour is not None:
            lines.append(f"Por jogador por hora: ~{compact_gold(result.share_per_hour)} gp.")
        split = damage_split(result.session)
        if split:
            lines.append("Damage Split: " + ", ".join(f"{name} - {percentage.normalize():f}%"
                                                       for name, percentage in split))
        lines.append("Saldo final: " + "; ".join(f"{player.name}: {share:,} gp"
                                                 for player, share in zip(result.session.players, result.shares)))
        return "\n".join(lines)


class ExpSharePanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(_label("Descubra os levels que podem compartilhar experiência com você.",
                                "pageDescription", wrap=True))
        row = QHBoxLayout()
        level_label = QLabel("Seu level")
        self.level_input = QSpinBox()
        self.level_input.setRange(1, 100_000)
        self.level_input.setValue(200)
        self.level_input.setFixedWidth(140)
        self.level_input.setAccessibleName("Seu level")
        level_label.setBuddy(self.level_input)
        row.addWidget(level_label)
        row.addWidget(self.level_input)
        row.addStretch()
        layout.addLayout(row)
        card = QFrame()
        card.setObjectName("card")
        box = QVBoxLayout(card)
        box.setContentsMargins(20, 18, 20, 18)
        box.setSpacing(8)
        box.addWidget(_label("Range para compartilhar", "mutedText"))
        self.range_label = _label("", "shareRange")
        box.addWidget(self.range_label)
        self.description = _label("", "mutedText", wrap=True)
        box.addWidget(self.description)
        layout.addWidget(card)
        layout.addWidget(_label(
            "O menor level deve atingir 2/3 do maior, com arredondamento para baixo. "
            "Em uma party, compare o menor e o maior level.", "mutedText", wrap=True))
        layout.addWidget(_label(
            "Também é preciso ativar o share, participar da hunt e estar a até 30 SQMs do líder, "
            "no mesmo andar ou um andar acima/abaixo.", "mutedText", wrap=True))
        self.level_input.valueChanged.connect(self._update_range)
        self._update_range()

    def _update_range(self) -> None:
        level = self.level_input.value()
        minimum, maximum = exp_share_range(level)
        self.range_label.setText(f"{minimum} – {maximum}")
        self.description.setText(f"Level {level} pode compartilhar com levels {minimum} a {maximum}.")


class ToolsPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("appPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)
        heading = QHBoxLayout()
        heading.setSpacing(24)
        heading.addWidget(_label("Tools", "pageTitle"))
        self.rashid_header = QWidget()
        rashid = QHBoxLayout(self.rashid_header)
        rashid.setContentsMargins(0, 0, 0, 0)
        rashid.setSpacing(4)
        art = QLabel()
        art.setFixedSize(40, 40)
        art.setAccessibleName("Rashid animado")
        self.rashid_movie = QMovie(str(ASSETS / "imgs" / "rashid.gif"), parent=self)
        self.rashid_movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self.rashid_movie.setScaledSize(QSize(40, 40))
        art.setMovie(self.rashid_movie)
        rashid.addWidget(art)
        self.rashid_title = QPushButton()
        self.rashid_title.setObjectName("rashidLink")
        self.rashid_title.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self._rashid_stop.map_url)))
        rashid.addWidget(self.rashid_title)
        heading.addWidget(self.rashid_header)
        heading.addStretch()
        layout.addLayout(heading)
        layout.addWidget(_label("Prepare a party, acerte a hunt e encontre o Rashid.", "pageDescription", wrap=True))
        self.scroll = QScrollArea()
        self.scroll.setObjectName("detailsScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        content.setObjectName("appPage")
        body = QVBoxLayout(content)
        body.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        body.setContentsMargins(0, 0, 6, 0)
        body.setSpacing(14)
        selection = QHBoxLayout()
        selection.setSpacing(8)
        self.tool_buttons = []
        self.tool_group = QButtonGroup(self)
        self.tool_pages = _ToolStack()
        self.loot_split = LootSplitPanel()
        self.exp_share = ExpSharePanel()
        for index, (name, page) in enumerate((("Loot Split", self.loot_split), ("EXP Share", self.exp_share))):
            self.tool_pages.addWidget(page)
            button = QPushButton(name)
            button.setObjectName("toolTab")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, target=index: self.tool_pages.setCurrentIndex(target))
            self.tool_group.addButton(button, index)
            self.tool_buttons.append(button)
            selection.addWidget(button)
        self.tool_buttons[0].setChecked(True)
        selection.addStretch()
        body.addLayout(selection)
        body.addWidget(self.tool_pages)
        body.addStretch()
        self.scroll.setWidget(content)
        layout.addWidget(self.scroll, 1)
        self.loot_split.calculated.connect(lambda: QTimer.singleShot(0, self._show_results))
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(30_000)
        self.refresh_timer.timeout.connect(self.refresh_rashid)
        self.refresh_rashid()

    def _show_results(self) -> None:
        if self.loot_split.result is not None and self.tool_pages.currentWidget() is self.loot_split:
            top = self.loot_split.results.mapTo(self.scroll.widget(), QPoint(0, 0)).y()
            self.scroll.verticalScrollBar().setValue(top)

    def refresh_rashid(self) -> None:
        stop, next_save = rashid_today()
        self._rashid_stop = stop
        self.rashid_title.setText(f"Rashid · {stop.city} ↗")
        self.rashid_title.setAccessibleName(f"Rashid em {stop.city}. Abrir localização no mapa.")
        local_save = next_save.astimezone()
        details = (
            f"{stop.weekday} no Tibia · {stop.city}\n{stop.directions}\n"
            f"Próxima troca às {local_save:%H:%M} (horário local).\n"
            "Server save: 10:00 CET/CEST, horário da Alemanha.\n"
            "Clique para abrir a localização no TibiaMaps."
        )
        self.rashid_header.setToolTip(details)
        self.rashid_title.setToolTip(details)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.refresh_rashid()
        self.refresh_timer.start()
        self.rashid_movie.start()

    def hideEvent(self, event) -> None:
        self.refresh_timer.stop()
        self.rashid_movie.stop()
        super().hideEvent(event)

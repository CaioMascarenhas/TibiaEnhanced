"""Cards de alertas sonoros iniciados pelo usuário."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt, QTimer, QUrl
from PySide6.QtGui import QKeySequence, QPainter, QPixmap, QShortcut
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QDialog, QFileDialog, QFormLayout, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QKeySequenceEdit, QLineEdit, QMessageBox, QPushButton, QScrollArea, QSpinBox,
    QVBoxLayout, QWidget,
)

from ..services.audio_timer import AudioTimer
from .design import ToggleCheckBox, heading_font, icon
from .design import CompactSlider as QSlider
from .dialog_shell import StyledDialog


ASSETS = Path(__file__).resolve().parents[1]
DEFAULT_TIMERS = (
    ("Foods 1h", 3600, ASSETS / "audios" / "foodacabou.mp3",
     tuple(sorted((ASSETS / "imgs" / "foods_1hr").glob("*.png")))),
    ("Potions 10min", 600, ASSETS / "audios" / "potionacabou.mp3",
     tuple(sorted((ASSETS / "imgs" / "potions_10min").glob("*.png")))),
)


def _clock_text(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{secs:02}" if hours else f"{minutes:02}:{secs:02}"


def _combined_image(paths: tuple[Path, ...]) -> QPixmap:
    """Compõe os itens de uma categoria em uma imagem para o card."""
    image = QPixmap(112, 72)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    count = len(paths)
    if count:
        size = min(48, (image.width() - 8 - 3 * (count - 1)) // count)
        gap = 3
        width = count * size + (count - 1) * gap
        left = (image.width() - width) // 2
        for index, path in enumerate(paths):
            source = QPixmap(str(path))
            if not source.isNull():
                scaled = source.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
                x = left + index * (size + gap) + (size - scaled.width()) // 2
                y = (image.height() - scaled.height()) // 2
                painter.drawPixmap(x, y, scaled)
    painter.end()
    return image


class TimerDialog(StyledDialog):
    def __init__(self, panel: AudioPanel, timer: AudioTimer | None = None) -> None:
        super().__init__(panel, "Editar temporizador" if timer else "Novo timer")
        self.panel = panel
        self.timer = timer
        self.setMinimumWidth(430)
        layout = self.content_layout
        form = QFormLayout()
        form.setSpacing(9)
        self.name_input = QLineEdit(timer.name if timer else "")
        self.name_input.setPlaceholderText("Ex.: Boost")
        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 86400)
        self.duration_input.setSuffix(" segundos")
        self.duration_input.setValue(timer.duration_seconds if timer else 600)
        self.sound_input = QLineEdit(str(timer.sound_file) if timer else "")
        browse = QPushButton("Escolher…")
        browse.setIcon(icon("plus", size=15))
        browse.clicked.connect(self._browse)
        sound_row = QHBoxLayout()
        sound_row.addWidget(self.sound_input, 1)
        sound_row.addWidget(browse)
        self.volume_input = QSlider(Qt.Orientation.Horizontal, accent="#4ba6ff")
        self.volume_input.setRange(0, 100)
        self.volume_input.setValue(round(timer.volume * 100) if timer else 100)
        self.loop_input = ToggleCheckBox("Reiniciar automaticamente")
        self.loop_input.setToolTip("Reiniciar automaticamente ao terminar")
        self.loop_input.setChecked(timer.loop if timer else False)
        self.shortcut_input = QKeySequenceEdit()
        self.shortcut_input.setKeySequence(QKeySequence(timer.shortcut if timer else ""))
        self.shortcut_input.setMaximumSequenceLength(1)
        clear_shortcut = QPushButton("Limpar")
        clear_shortcut.clicked.connect(self.shortcut_input.clear)
        shortcut_row = QHBoxLayout()
        shortcut_row.addWidget(self.shortcut_input, 1)
        shortcut_row.addWidget(clear_shortcut)
        form.addRow("Nome", self.name_input)
        form.addRow("Duração", self.duration_input)
        form.addRow("Som (.mp3/.wav)", sound_row)
        form.addRow("Volume", self.volume_input)
        form.addRow("Loop", self.loop_input)
        form.addRow("Tecla para reiniciar", shortcut_row)
        layout.addLayout(form)
        hint = QLabel("O atalho funciona enquanto a janela do aplicativo está em foco.")
        hint.setObjectName("mutedText")
        layout.addWidget(hint)
        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Salvar")
        save.setObjectName("primaryButton")
        save.setIcon(icon("plus", "#ffffff", 15))
        save.clicked.connect(self._validate)
        actions.addWidget(cancel)
        actions.addWidget(save)
        layout.addLayout(actions)

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar áudio", "", "Áudio (*.mp3 *.wav)")
        if path:
            self.sound_input.setText(path)

    def _validate(self) -> None:
        path = Path(self.sound_input.text().strip())
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Nome obrigatório", "Informe um nome para o temporizador.")
        elif path.suffix.lower() not in {".mp3", ".wav"} or not path.is_file():
            QMessageBox.warning(self, "Áudio inválido", "Escolha um arquivo .mp3 ou .wav existente.")
        elif self.panel.shortcut_conflict(self.shortcut_input.keySequence(), self.timer):
            QMessageBox.warning(self, "Atalho em uso", "Essa tecla já está vinculada a outro temporizador.")
        else:
            self.accept()


class TimerCard(QFrame):
    def __init__(self, timer: AudioTimer, panel: AudioPanel, *, removable: bool = True) -> None:
        super().__init__()
        self.timer = timer
        self.panel = panel
        self.removable = removable
        self.setObjectName("timerCard")
        self.setFixedHeight(182)
        self.audio_output = QAudioOutput(self)
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(QUrl.fromLocalFile(str(timer.sound_file.resolve())))
        self.shortcut_binding = QShortcut(self)
        self.shortcut_binding.setContext(Qt.ShortcutContext.WindowShortcut)
        self.shortcut_binding.setAutoRepeat(False)
        self.shortcut_binding.activated.connect(self._restart_and_start)
        self._update_shortcut()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        row = QHBoxLayout()
        self.art = QLabel()
        self.art.setFixedSize(76, 48)
        self.art.setPixmap(_combined_image(timer.images).scaled(
            76, 48, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation))
        row.addWidget(self.art)
        details = QVBoxLayout()
        details.setSpacing(0)
        self.title = QLabel(timer.name)
        self.title.setObjectName("timerTitle")
        self.countdown = QLabel()
        self.countdown.setObjectName("timerCountdown")
        details.addWidget(self.title)
        details.addWidget(self.countdown)
        row.addLayout(details, 1)
        layout.addLayout(row)
        self.status = QLabel()
        self.status.setObjectName("mutedText")
        options = QHBoxLayout()
        options.addWidget(self.status)
        options.addStretch()
        self.loop_check = ToggleCheckBox("Loop")
        self.loop_check.setToolTip("Reiniciar automaticamente ao terminar")
        self.loop_check.setChecked(timer.loop)
        self.loop_check.toggled.connect(self._set_loop)
        options.addWidget(self.loop_check)
        layout.addLayout(options)
        volume_row = QHBoxLayout()
        volume_icon = QLabel()
        volume_icon.setPixmap(icon("volume-2", size=14).pixmap(14, 14))
        volume_row.addWidget(volume_icon)
        self.volume = QSlider(Qt.Orientation.Horizontal, accent="#4ba6ff")
        self.volume.setRange(0, 100)
        self.volume.setValue(round(timer.volume * 100))
        self.volume.valueChanged.connect(self._set_volume)
        volume_row.addWidget(self.volume, 1)
        self.volume_label = QLabel(f"{self.volume.value()}%")
        self.volume_label.setObjectName("mutedText")
        volume_row.addWidget(self.volume_label)
        layout.addLayout(volume_row)
        buttons = QHBoxLayout()
        buttons.setSpacing(3)
        self.start_button = QPushButton("Iniciar")
        self.start_button.setObjectName("primaryButton")
        self.start_button.clicked.connect(self._toggle)
        buttons.addWidget(self.start_button)
        buttons.addStretch()
        actions = [
            ("rotate-ccw", "Zerar temporizador", self._reset),
            ("volume-2", "Testar som", self.play_sound),
            ("pencil", "Editar temporizador e atalho", self._edit),
        ]
        if self.removable:
            actions.append(("trash", "Excluir temporizador", lambda: panel.remove_card(self)))
        for name, tooltip, callback in actions:
            button = QPushButton()
            button.setObjectName("iconButton")
            button.setFixedSize(25, 26)
            button.setIcon(icon(name, size=14))
            button.setToolTip(tooltip)
            button.setAccessibleName(tooltip)
            button.clicked.connect(callback)
            buttons.addWidget(button)
        layout.addLayout(buttons)
        self.shortcut_label = QLabel()
        self.shortcut_label.setObjectName("mutedText")
        layout.addWidget(self.shortcut_label)
        self._update_shortcut()
        self.refresh()

    def _set_loop(self, enabled: bool) -> None:
        self.timer.loop = enabled

    def _update_shortcut(self) -> None:
        self.shortcut_binding.setKey(QKeySequence(self.timer.shortcut))
        self.shortcut_binding.setEnabled(bool(self.timer.shortcut))
        if hasattr(self, "shortcut_label"):
            self.shortcut_label.setText(
                f"Atalho: {self.timer.shortcut}" if self.timer.shortcut else "Sem atalho"
            )

    def _restart_and_start(self) -> None:
        self.timer.reset()
        self.timer.start()
        self.refresh()

    def _set_volume(self, value: int) -> None:
        self.timer.volume = value / 100
        self.volume_label.setText(f"{value}%")
        self.panel.update_audio_volumes()

    def _toggle(self) -> None:
        if self.timer.running:
            self.timer.pause()
        else:
            self.timer.start()
        self.refresh()

    def _reset(self) -> None:
        self.timer.reset()
        self.refresh()

    def _edit(self) -> None:
        dialog = TimerDialog(self.panel, self.timer)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.timer.name = dialog.name_input.text().strip()
        self.timer.duration_seconds = dialog.duration_input.value()
        self.timer.sound_file = Path(dialog.sound_input.text().strip())
        self.timer.volume = dialog.volume_input.value() / 100
        self.timer.loop = dialog.loop_input.isChecked()
        self.timer.shortcut = dialog.shortcut_input.keySequence().toString(
            QKeySequence.SequenceFormat.PortableText
        )
        self.timer.reset()
        self.player.setSource(QUrl.fromLocalFile(str(self.timer.sound_file.resolve())))
        self.title.setText(self.timer.name)
        self.volume.setValue(dialog.volume_input.value())
        self.loop_check.setChecked(self.timer.loop)
        self._update_shortcut()
        self.refresh()

    def play_sound(self) -> None:
        self.player.stop()
        self.player.play()

    def refresh(self) -> None:
        self.countdown.setText(_clock_text(self.timer.remaining()))
        if self.timer.running:
            self.status.setText("Em andamento")
            self.start_button.setText("Pausar")
            self.start_button.setIcon(icon("pause", "#ffffff", 15))
        elif self.timer.finished:
            self.status.setText("Concluído")
            self.start_button.setText("Iniciar")
            self.start_button.setIcon(icon("play", "#ffffff", 15))
        elif self.timer.remaining() < self.timer.duration_seconds:
            self.status.setText("Pausado")
            self.start_button.setText("Retomar")
            self.start_button.setIcon(icon("play", "#ffffff", 15))
        else:
            self.status.setText("Pronto")
            self.start_button.setText("Iniciar")
            self.start_button.setIcon(icon("play", "#ffffff", 15))


class AudioPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("appPage")
        self.cards: list[TimerCard] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        heading = QHBoxLayout()
        title = QLabel("Temporizadores")
        title.setObjectName("pageTitle")
        title.setFont(heading_font(19))
        heading.addWidget(title)
        heading.addStretch()
        create = QPushButton("Novo timer")
        create.setObjectName("primaryButton")
        create.setIcon(icon("plus", "#ffffff", 16))
        create.setIconSize(QSize(16, 16))
        create.clicked.connect(self._create)
        heading.addWidget(create)
        layout.addLayout(heading)
        volume_row = QHBoxLayout()
        volume_icon = QLabel()
        volume_icon.setPixmap(icon("volume-2", "#b6cfe3", 18).pixmap(18, 18))
        volume_row.addWidget(volume_icon)
        volume_row.addWidget(QLabel("Volume geral"))
        self.master_volume = QSlider(Qt.Orientation.Horizontal, accent="#4ba6ff")
        self.master_volume.setRange(0, 100)
        self.master_volume.setValue(50)
        self.master_volume.setMaximumWidth(180)
        self.master_volume.valueChanged.connect(self.update_audio_volumes)
        volume_row.addWidget(self.master_volume)
        self.master_label = QLabel()
        volume_row.addWidget(self.master_label)
        volume_row.addStretch()
        layout.addLayout(volume_row)

        scroll = QScrollArea()
        scroll.setObjectName("detailsScroll")
        scroll.setWidgetResizable(True)
        container = QWidget()
        container.setObjectName("appPage")
        self.card_layout = QGridLayout(container)
        self.card_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.card_layout.setContentsMargins(0, 0, 8, 0)
        self.card_layout.setSpacing(9)
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        for name, duration, sound, images in DEFAULT_TIMERS:
            self.add_timer(AudioTimer(name, duration, sound, images=images), removable=False)
        self.update_audio_volumes()
        self.ticker = QTimer(self)
        self.ticker.setInterval(200)
        self.ticker.timeout.connect(self._tick)
        self.ticker.start()

    def add_timer(self, timer: AudioTimer, *, removable: bool = True) -> TimerCard:
        if self.shortcut_conflict(QKeySequence(timer.shortcut)):
            raise ValueError("Atalho já usado por outro temporizador")
        card = TimerCard(timer, self, removable=removable)
        self.cards.append(card)
        self._reflow_cards()
        self.update_audio_volumes()
        return card

    def remove_card(self, card: TimerCard) -> None:
        if card not in self.cards or not card.removable:
            return
        card.timer.reset()
        card.player.stop()
        self.cards.remove(card)
        self.card_layout.removeWidget(card)
        card.deleteLater()
        self._reflow_cards()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._reflow_cards()

    def _reflow_cards(self) -> None:
        columns = max(1, self.width() // 280)
        while self.card_layout.count():
            self.card_layout.takeAt(0)
        for index, card in enumerate(self.cards):
            self.card_layout.addWidget(card, index // columns, index % columns)
        rows = (len(self.cards) + columns - 1) // columns
        self.card_layout.parentWidget().setMinimumHeight(max(0, rows * 191 - 9))

    def _create(self) -> None:
        dialog = TimerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.add_timer(AudioTimer(
                dialog.name_input.text().strip(), dialog.duration_input.value(),
                Path(dialog.sound_input.text().strip()), dialog.volume_input.value() / 100,
                loop=dialog.loop_input.isChecked(),
                shortcut=dialog.shortcut_input.keySequence().toString(
                    QKeySequence.SequenceFormat.PortableText
                ),
            ))

    def shortcut_conflict(self, sequence: QKeySequence, editing: AudioTimer | None = None) -> bool:
        if sequence.isEmpty():
            return False
        return any(
            card.timer is not editing and QKeySequence(card.timer.shortcut) == sequence
            for card in self.cards
        )

    def update_audio_volumes(self) -> None:
        self.master_label.setText(f"{self.master_volume.value()}%")
        for card in self.cards:
            card.audio_output.setVolume(self.master_volume.value() / 100 * card.timer.volume)

    def _tick(self) -> None:
        for card in self.cards:
            if card.timer.tick():
                card.play_sound()
            card.refresh()

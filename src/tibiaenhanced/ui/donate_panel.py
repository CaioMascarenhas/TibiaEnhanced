"""Doações voluntárias por Tibia Coins ou Pix."""

from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
                               QPushButton, QScrollArea, QVBoxLayout, QWidget)

from .design import ASSETS


CHARACTER = "Mascarenhas The Great"
PIX_KEY = "f91fe6b8-2c7e-4308-83b8-6a9774969ef6"
PIX_RECEIVER = "CAIO MASCARENHAS SOARES"
PIX_PAYLOAD = (
    "00020101021126580014br.gov.bcb.pix0136f91fe6b8-2c7e-4308-83b8-6a9774969ef6"
    "5204000053039865802BR5923CAIO MASCARENHAS SOARES6006MACEIO62070503***6304F0D3"
)


class DonatePanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("appPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        heading = QVBoxLayout()
        heading.setSpacing(5)
        title = QLabel("Apoie o projeto")
        title.setObjectName("pageTitle")
        heading.addWidget(title)
        subtitle = QLabel(
            "O app é 100% gratuito. A doação é voluntária, apenas para quem quiser apoiar o projeto."
        )
        subtitle.setObjectName("pageDescription")
        subtitle.setWordWrap(True)
        heading.addWidget(subtitle)
        layout.addLayout(heading)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("detailsScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container = QWidget()
        container.setObjectName("appPage")
        cards = QGridLayout(container)
        self.cards_layout = cards
        cards.setContentsMargins(0, 0, 6, 0)
        cards.setSpacing(16)
        cards.setAlignment(Qt.AlignmentFlag.AlignTop)

        details = QFrame()
        self.details_card = details
        details.setObjectName("card")
        info = QVBoxLayout(details)
        info.setContentsMargins(20, 18, 20, 18)
        info.setSpacing(12)
        coins = QLabel("Tibia Coins")
        coins.setObjectName("sectionTitle")
        info.addWidget(coins)
        self.character_label = self._selectable(CHARACTER)
        info.addWidget(self.character_label)
        self.copy_character_button = self._copy_button("Copiar personagem", CHARACTER)
        info.addWidget(self.copy_character_button)
        info.addSpacing(8)
        pix = QLabel("Pix")
        pix.setObjectName("sectionTitle")
        info.addWidget(pix)
        receiver = self._selectable(PIX_RECEIVER.title())
        receiver.setObjectName("mutedText")
        info.addWidget(receiver)
        self.key_label = self._selectable(PIX_KEY)
        info.addWidget(self.key_label)
        self.copy_pix_button = self._copy_button("Copiar chave Pix", PIX_KEY)
        self.copy_pix_button.setObjectName("primaryButton")
        info.addWidget(self.copy_pix_button)
        self.copy_code_button = self._copy_button("Copiar código Pix", PIX_PAYLOAD)
        info.addWidget(self.copy_code_button)
        info.addStretch()
        qr_card = QFrame()
        self.qr_card = qr_card
        qr_card.setObjectName("card")
        qr_layout = QVBoxLayout(qr_card)
        qr_layout.setContentsMargins(20, 18, 20, 18)
        qr_layout.setSpacing(12)
        qr_title = QLabel("QR Code Pix")
        qr_title.setObjectName("sectionTitle")
        qr_layout.addWidget(qr_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.qr_label = QLabel()
        self.qr_label.setAccessibleName("QR Code Pix para Caio Mascarenhas Soares")
        self.qr_label.setPixmap(QPixmap(str(ASSETS / "imgs" / "donate-pix.png")).scaled(
            224, 224, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation))
        qr_layout.addWidget(self.qr_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        hint = QLabel("Leia com o app do seu banco.\nVocê escolhe o valor ao pagar.")
        hint.setObjectName("mutedText")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_layout.addWidget(hint)
        self.scroll.setWidget(container)
        layout.addWidget(self.scroll, 1)
        self.scroll.viewport().installEventFilter(self)
        self._reflow_cards()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._reflow_cards()

    def eventFilter(self, watched, event) -> bool:
        if watched is self.scroll.viewport() and event.type() == QEvent.Type.Resize:
            self._reflow_cards()
        return super().eventFilter(watched, event)

    def _reflow_cards(self) -> None:
        available = (self.scroll.maximumViewportSize().width()
                     - self.scroll.verticalScrollBar().sizeHint().width() - 6)
        required = (self.details_card.minimumSizeHint().width()
                    + self.qr_card.minimumSizeHint().width() + self.cards_layout.spacing())
        horizontal = available >= max(600, required)
        if horizontal == getattr(self, "_horizontal_cards", None):
            return
        self._horizontal_cards = horizontal
        self.cards_layout.removeWidget(self.details_card)
        self.cards_layout.removeWidget(self.qr_card)
        self.cards_layout.addWidget(self.details_card, 0, 0)
        self.cards_layout.addWidget(self.qr_card, 0 if horizontal else 1, 1 if horizontal else 0)
        self.cards_layout.setColumnStretch(0, 1)
        self.cards_layout.setColumnStretch(1, 0)

    @staticmethod
    def _selectable(text: str) -> QLabel:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse |
                                      Qt.TextInteractionFlag.TextSelectableByKeyboard)
        return label

    def _copy_button(self, caption: str, value: str) -> QPushButton:
        button = QPushButton(caption)
        button.setAccessibleName(caption)
        reset = QTimer(button)
        reset.setSingleShot(True)
        reset.setInterval(1800)
        reset.timeout.connect(lambda: button.setText(caption))

        def copy() -> None:
            QApplication.clipboard().setText(value)
            button.setText("Copiado!")
            reset.start()

        button.clicked.connect(copy)
        return button

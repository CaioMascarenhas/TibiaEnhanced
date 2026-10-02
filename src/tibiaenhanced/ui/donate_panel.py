"""Doações voluntárias por Tibia Coins ou Pix."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
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
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        title = QLabel("Apoie o Tibia Enhanced")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        subtitle = QLabel(
            "O app é 100% gratuito. A doação é voluntária, apenas para quem quiser apoiar o projeto."
        )
        subtitle.setObjectName("mutedText")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("detailsScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container = QWidget()
        container.setObjectName("appPage")
        cards = QHBoxLayout(container)
        cards.setContentsMargins(0, 0, 8, 0)
        cards.setSpacing(10)
        cards.setAlignment(Qt.AlignmentFlag.AlignTop)

        details = QFrame()
        details.setObjectName("card")
        info = QVBoxLayout(details)
        info.setContentsMargins(14, 12, 14, 12)
        info.setSpacing(8)
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
        receiver = self._selectable(PIX_RECEIVER)
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
        cards.addWidget(details, 1)

        qr_card = QFrame()
        qr_card.setObjectName("card")
        qr_layout = QVBoxLayout(qr_card)
        qr_layout.setContentsMargins(12, 12, 12, 12)
        qr_layout.setSpacing(8)
        qr_title = QLabel("QR Code Pix")
        qr_title.setObjectName("sectionTitle")
        qr_layout.addWidget(qr_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.qr_label = QLabel()
        self.qr_label.setAccessibleName("QR Code Pix para Caio Mascarenhas Soares")
        self.qr_label.setPixmap(QPixmap(str(ASSETS / "imgs" / "donate-pix.png")))
        qr_layout.addWidget(self.qr_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        hint = QLabel("Leia com o app do seu banco.\nVocê escolhe o valor ao pagar.")
        hint.setObjectName("mutedText")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_layout.addWidget(hint)
        cards.addWidget(qr_card)
        self.scroll.setWidget(container)
        layout.addWidget(self.scroll, 1)

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

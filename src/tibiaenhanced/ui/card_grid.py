"""Grade responsiva sem reconstruir o layout a cada pixel de redimensionamento."""

from PySide6.QtWidgets import QGridLayout, QScrollArea, QWidget


def arrange_cards(scroll: QScrollArea, layout: QGridLayout,
                  cards: list[QWidget], column_width: int) -> None:
    if getattr(layout, "_arranging", False):
        return
    layout._arranging = True
    try:
        # Reserve the scrollbar gutter even when it is hidden. Otherwise a new
        # column can hide the scrollbar, changing the width and columns again.
        margins = layout.contentsMargins()
        available = (scroll.maximumViewportSize().width()
                     - scroll.verticalScrollBar().sizeHint().width()
                     - margins.left() - margins.right())
        columns = max(1, (max(1, available) + layout.spacing()) // column_width)
        topology = (columns, tuple(cards))
        if topology != getattr(layout, "_card_topology", None):
            for card in cards:
                layout.removeWidget(card)
            for index, card in enumerate(cards):
                layout.addWidget(card, index // columns, index % columns)
            layout._card_topology = topology
        # Font/theme changes can affect size hints without changing the grid.
        rows = [max(max(card.minimumHeight(), card.sizeHint().height())
                    for card in cards[start:start + columns])
                for start in range(0, len(cards), columns)]
        height = (sum(rows) + max(0, len(rows) - 1) * layout.spacing()
                  + margins.top() + margins.bottom())
        if layout.parentWidget().minimumHeight() != height:
            layout.parentWidget().setMinimumHeight(height)
    finally:
        layout._arranging = False

from typing import Optional, Tuple

import urwid

from Models.item import Item
from Views.hex_row import HexRow


class UnknownArea(Item):

    def __init__(self, image, address, size):
        super().__init__(image, address, size, 'Unknown')

    def get_view(self, vid: Optional[Tuple[urwid.SimpleListWalker, int]] = None):
        super().get_view(vid)




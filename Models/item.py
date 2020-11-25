from typing import Tuple, Optional

import urwid

from Models.programimage import ProgramImage


class Item:
    image: ProgramImage
    start_address: int
    end_address: int
    item_type: str

    @property
    def size(self):
        return self.end_address - self.start_address

    view_id: Optional[Tuple[urwid.SimpleListWalker, int]]

    def __init__(self, image, start, end, item_type):
        self.image = image
        self.start_address = start
        self.end_address = end
        self.item_type = item_type

        self.view_id = None

    def get_view(self, vid: Optional[Tuple[urwid.SimpleListWalker, int]] = None):
        self.view_id = vid



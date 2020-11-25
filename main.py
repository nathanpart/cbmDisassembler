# This is a sample Python script.

import urwid

from Models.programimage import ProgramImage
from Views.hex_row import HexRow
from Views.palette import palette


def main():
    image = ProgramImage()

    for i in range(0, 256):
        image[i] = i

    pile = urwid.Pile([
        (1, HexRow(image, 0x0000, 0x0010)),
        (1, HexRow(image, 0x0010, 0x0020)),
        (1, HexRow(image, 0x0020, 0x0030)),
        (1, HexRow(image, 0x0035, 0x0040)),
        (1, HexRow(image, 0x0040, 0x0050)),
        (1, HexRow(image, 0x0050, 0x0060)),
        (1, HexRow(image, 0x0060, 0x0070)),
        (1, HexRow(image, 0x0070, 0x0080)),
    ])
    fill = urwid.AttrWrap(urwid.Filler(pile, 'top'), 'normal')

    loop = urwid.MainLoop(
        fill,
        palette
    )
    loop.run()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

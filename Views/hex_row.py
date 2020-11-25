from typing import Dict, List

import urwid

from Models.programimage import ProgramImage
from Controller.messenging import send_message, connect_listener


class HexDigit(urwid.WidgetWrap):
    is_undefined: bool
    value: int
    undefined_ch: str

    def selectable(self):
        return not self.is_undefined

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def rows(self, size, focus=False):
        return 1

    def __init__(self, value: int, is_undefined=False, undefined_ch='  '):
        self.is_undefined = is_undefined
        self.value = value
        normal_attr = 'hidden' if self.is_undefined else 'hex_byte'
        focus_attr = 'hidden' if self.is_undefined else 'hex_byte_sel'
        value_str = undefined_ch if self.is_undefined else '{:02X}'.format(self.value)

        super().__init__(urwid.AttrMap(urwid.Text(value_str), normal_attr, focus_attr))


class HexChar(urwid.WidgetWrap):
    address: int
    is_undefined: bool
    value: int
    undefined_ch: str
    attr_widget: urwid.AttrMap

    def _focus_address(self, address: int):
        if self.address == address and not self.is_undefined:
            self.attr_widget.set_attr_map({None: 'hex_char_sel'})
        else:
            self.attr_widget.set_attr_map({None: 'hex_char'})
        self._invalidate()

    def __init__(self, value: int, address: int, is_undefined=False, undefined_ch=' '):
        self.address = address
        self.is_undefined = is_undefined
        self.value = value
        self.undefined_ch = undefined_ch
        char_attr = 'hidden' if self.is_undefined else ('hex_char_sel' if self.is_focussed else 'hex_byte')
        value_str = self.undefined_ch if self.is_undefined else (chr(value) if 0x20 <= value < 0x7F else '.')
        self.attr_widget = urwid.AttrMap(urwid.Text(value_str), char_attr)

        super().__init__(self.attr_widget)

        if not self.is_undefined:
            connect_listener('focus_address', self._focus_address)


class HexAddress(urwid.WidgetWrap):
    start_address: int
    end_address: int
    attr_widget: urwid.AttrMap

    def _focus_address(self, address):
        if self.start_address <= address < self.end_address:
            self.attr_widget.set_attr_map({None: 'addr_field_sel'})
        else:
            self.attr_widget.set_attr_map({None: 'addr_field'})
        self._invalidate()

    def __init__(self, start_address: int, end_address: int):
        self.start_address = start_address
        self.end_address = end_address
        address_attr = 'addr_field'
        address_str = '{:04X}'.format(self.start_address)
        self.attr_widget = urwid.AttrMap(urwid.Text(address_str), address_attr)

        super().__init__(self.attr_widget)

        connect_listener('focus_address', self._focus_address)


class BlankSpace(urwid.WidgetWrap):

    def _init__(self, length=1):
        spaces = ' ' * length
        super().__init__(urwid.Text((spaces, 'hidden')))

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def rows(self, size, focus=False):
        return 1


class HexRow(urwid.Columns):
    char_widgets: List[HexChar]
    focus_addresses: Dict[int, int]

    def __init__(self, image: ProgramImage, start_address: int, end_address: int):
        widget_list = list()

        widget_list.append((5, HexAddress(start_address, end_address)))
        widget_list.append((1, BlankSpace()))

        self.focus_addresses = dict()
        self.char_widgets = list()
        position = 2
        for i in range(0, 16 if start_address + 16 < len(image) else (len(image) - start_address)):
            widget_list.append((2, HexDigit(image[start_address + i], end_address >= start_address + i)))
            if (start_address + i) < end_address:
                self.focus_addresses[position] = start_address + i
            self.char_widgets.append(HexChar(image[start_address + i], start_address + i,
                                             end_address >= start_address + i))
            position += 2

            if i != 7:
                widget_list.append((1, BlankSpace()))
            else:
                widget_list.append((1, urwid.Text(('-', 'hex_sep'))))

        widget_list.append((2, urwid.Text((' |', 'hex_sep'))))
        for char_widget in self.char_widgets:
            widget_list.append((1, char_widget))
        widget_list.append((1, urwid.Text(('|', 'hex_sep'))))

        super().__init__(widget_list)

    def _set_focus_position(self, position):
        super()._set_focus_position(position)
        for focus_pos, focus_address in self.focus_addresses.items():
            if self.focus_position == focus_pos:
                send_message('focus_address', self.focus_addresses[focus_pos])
        self._invalidate()


class OpCodeColumns(urwid.Columns):
    focus_addresses: Dict[int, int]

    def __init__(self, image: ProgramImage, start_address: int, end_address: int):
        widget_list = list()

        self.focus_positions = dict()
        self.focus_addresses = dict()
        for i, address in enumerate(range(start_address, end_address)):
            widget_list.append(('pack', HexDigit(image[address])))
            self.focus_addresses[i] = address  # Blank spaces are not to focusable

        super().__init__(widget_list, 1)

    def _set_focus_position(self, position):
        super()._set_focus_position(position)
        for focus_pos, focus_address in self.focus_addresses.items():
            if self.focus_position == focus_pos:
                assert focus_pos in self.focus_addresses
                send_message('focus_address', self.focus_addresses[focus_pos])
        self._invalidate()


class Operand(urwid.WidgetWrap):
    address: int
    operand_text: urwid.Text
    operand_attr: urwid.AttrMap

    def __init__(self, address: int, text=''):
        self.address = address
        self.operand_text = urwid.Text(text)
        self.operand_attr = urwid.AttrMap(self.operand_text, 'operand')

        super().__init__(self.operand_attr)

        connect_listener('focus_address', self._focus_address)
        connect_listener('set_operand_text', self._set_operand_text)

    def _focus_address(self, address: int):
        if self.address == address:
            self.attr_widget.set_attr_map({None: 'operand_sel'})
        else:
            self.attr_widget.set_attr_map({None: 'operand'})
        self._invalidate()

    def _set_operand_text(self, address: int, text: str):
        if address == self.address:
            self.operand_text.set_text(text)


class OperandLine(urwid.Columns):

    def __init__(self, start_address, end_address):
        operand = list()
        for address in range(start_address, end_address):
            operand.append('pack', Operand(address))
        super().__init__(operand)


class LabelText(urwid.WidgetWrap):
    label_text: urwid.Text
    address: int

    def __init__(self, address: int, text=''):
        self.address = address
        self.label_text = urwid.Text(text)
        super().__init__(urwid.WidgetWrap(self.label_text), 'label')

        connect_listener('label_text', self._set_label)

    def _set_label(self, address: int, label: str):
        if address == self.address:
            self.label_text.set_text(label)


class OpCodeText(urwid.WidgetWrap):
    op_code_text: urwid.Text
    address: int

    def __init__(self, address: int, text=''):
        self.address = address
        self.label_text = urwid.Text(text)
        super().__init__(urwid.WidgetWrap(self.op_code_text), 'op_code_text')

        connect_listener('op_code_text', self._set_op_code_text)

    def _set_op_code_text(self, address: int, label: str):
        if address == self.address:
            self.op_code_text.set_text(label)


class CommentText(urwid.WidgetWrap):
    comment_text: urwid.Text
    address: int

    def __init__(self, address: int, comment=''):
        self.address = address
        self.comment_text = urwid.Text(comment)
        super().__init__(urwid.WidgetWrap(self.comment_text), 'comment_text')

        connect_listener('comment_text', self._set_comment_text)

    def _set_comment_text(self, address: int, comment: str):
        if address == self.address:
            self.comment_text.set_text(comment)


class DefinedRow(urwid.Columns):

    def __init__(self, image: ProgramImage, start_address: int, end_address: int):
        widget_list = list()

        widget_list.append((5, HexAddress(start_address, end_address)))
        widget_list.append((1, BlankSpace()))

        widget_list.append((24, OpCodeColumns(image, start_address, end_address)))
        widget_list.append((1, BlankSpace()))
        widget_list.append((10, LabelText(start_address)))  # Label column
        widget_list.append((1, BlankSpace()))
        widget_list.append((5, OpCodeText(start_address)))  # Opcode Text

        widget_list.append((1, BlankSpace()))
        widget_list.append(25, OperandLine(start_address, end_address))  # Operand
        widget_list.append((1, BlankSpace()))
        widget_list.append(50, CommentText(start_address))  # comment

        super().__init__(widget_list)

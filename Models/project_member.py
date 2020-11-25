from typing import Dict, List

from Controller.config import config
from Models.programimage import ProgramImage


class ProjectMember:
    images: Dict[str, ProgramImage]
    current_image: ProgramImage
    image_name: str
    machine_type: str
    machine_config: int
    cpu_type: str
    mappings: list
    mapping_table: List[Dict[str, list]]
    region_types: list
    region_list: list

    def __init__(self, name, machine):
        self.machine_type = machine
        self.image_name = name
        self.region_types = list()

        self.images = dict()
        self.images['RAM'] = ProgramImage()
        self.images['ROM'] = ProgramImage()
        self.images['IO'] = ProgramImage()
        self.images['NONE'] = ProgramImage()
        self.images['CROM'] = ProgramImage()

        self.cpu_type = '6510'

        if machine == 'C64':
            self.initC64()
        elif machine == 'C128':
            self.initC128()
        elif machine == '1541':
            self.init1541()
        elif machine == '1571':
            self.init1571()
        elif machine == '1581':
            self.init1581()
        else:
            self.region_list = [(0x0000, 0x10000)]
            self.mapping_table = [dict() for _ in range(0, len(self.region_list))]
            self.change_config(0)

    def change_config(self, mode: int):
        if self.machine_type == 'C64':
            new_map = self.get_c64_region(mode)
        elif self.machine_type == 'C128':
            new_map = self.get_c128_region(mode)
        elif self.machine_type == '1541':
            new_map = ['RAM', 'NONE', 'IO', 'NONE', 'IO', 'NONE', 'ROM']
        elif self.machine_type == '1571':
            new_map = ['RAM', 'NONE', 'IO', 'NONE', 'IO', 'NONE', 'IO', 'NONE', 'IO', 'NONE', 'ROM']
        elif self.machine_type == '1581':
            new_map = ['RAM', 'NONE', 'IO', 'ROM']
        else:
            new_map = ['RAM']
        if len(self.region_types) != 0:
            self.save_state()
        self.region_types = new_map
        self.load_state()
        self.machine_config = mode

    def save_state(self):
        region = 0
        element_list = [list() for _ in range(0, len(self.region_list))]

        for element in self.mappings:
            while region < len(self.region_list):
                if self.region_list[region][0] <= element.start_address < self.region_list[region][1]:
                    element_list[region].append(element)
                    break
                else:
                    region += 1
            else:
                raise IndexError('Elements found outside of scope.')

        for region in range(0, len(self.region_list)):
            name = self.region_types[0]
            self.mapping_table[region][name] = element_list[region]

    def load_state(self):
        self.mappings = list()
        for region in range(0, len(self.region_list)):
            if self.region_types[region] in self.mapping_table[region]:
                self.mappings += self.mapping_table[region][self.region_types[region]]
            start = self.region_list[region][0]
            end = self.region_list[region][1]
            self.current_image[start:end] = self.images[self.region_types[region]][start:end]

    def get_c64_region(self, mode: int):
        if mode > 31:
            raise ValueError('Commodore 64 has only 31 possible memory configuration.')
        if mode == 32:
            new_map = ['IO', 'RAM', 'RAM', 'RAM', 'ROM', 'RAM', 'IO', 'ROM']
        elif mode == 30 or mode == 14:
            new_map = ['IO', 'RAM', 'RAM', 'RAM', 'RAM', 'RAM', 'IO', 'ROM']
        elif mode == 29 or mode == 13 or mode == 5:
            new_map = ['IO', 'RAM', 'RAM', 'RAM', 'RAM', 'RAM', 'IO', 'RAM']
        elif mode == 28 or mode == 24 or mode == 12 or mode == 8 or mode == 4 or mode == 0 or mode == 1:
            new_map = ['IO', 'RAM', 'RAM', 'RAM', 'RAM', 'RAM', 'RAM', 'RAM']
        elif mode == 27:
            new_map = ['IO', 'RAM', 'RAM', 'RAM', 'ROM', 'RAM', 'ROM', 'ROM']
        elif mode == 26 or mode == 10:
            new_map = ['IO', 'RAM', 'RAM', 'RAM', 'RAM', 'RAM', 'ROM', 'ROM']
        elif mode == 25 or mode == 9:
            new_map = ['IO', 'RAM', 'RAM', 'RAM', 'RAM', 'RAM', 'ROM', 'RAM']
        elif mode == 15:
            new_map = ['IO', 'RAM', 'RAM', 'CROM', 'ROM', 'RAM', 'IO', 'ROM']
        elif mode == 11:
            new_map = ['IO', 'RAM', 'RAM', 'CROM', 'ROM', 'RAM', 'RAM', 'ROM']
        elif mode == 7:
            new_map = ['IO', 'RAM', 'RAM', 'CROM', 'CROM', 'RAM', 'IO', 'ROM']
        elif mode == 6:
            new_map = ['IO', 'RAM', 'RAM', 'RAM', 'CROM', 'RAM', 'IO', 'ROM']
        elif mode == 3:
            new_map = ['IO', 'RAM', 'RAM', 'CROM', 'CROM', 'RAM', 'ROM', 'ROM']
        elif mode == 2:
            new_map = ['IO', 'RAM', 'RAM', 'RAM', 'CROM', 'RAM', 'ROM', 'ROM']
        else:
            new_map = ['IO', 'RAM', 'NONE', 'CROM', 'NONE', 'NONE', 'IO', 'CROM']
        return new_map

    def get_c128_region(self, mode: int):
        common = (mode & 0xC00) >> 10
        common_size = (mode & 0x300) >> 8
        ram_bank = (mode & 0xC0) >> 6
        hi_rom = (mode & 0x30) >> 4
        mid_rom = (mode & 0x0C) >> 2
        lo_rom = (mode & 0x02) >> 1
        io_on = (mode & 0x01)

        ram = ['RAM', 'RAM1', 'RAM2', 'RAM3'][ram_bank]

        # Cpu I/O registers
        new_map = ['IO']

        # first 1K of RAM
        if common == 1 or common == 3:
            new_map.append('RAM')
        else:
            new_map.append(ram)

        # 1K to 4K
        if (common == 1 or common == 3) and common_size > 0:
            new_map.append('RAM')
        else:
            new_map.append(ram)

        # 4K to 8K
        if (common == 1 or common == 3) and common_size > 1:
            new_map.append('RAM')
        else:
            new_map.append(ram)

        # 4K to 16K
        if (common == 1 or common == 3) and common_size == 3:
            new_map.append('RAM')
        else:
            new_map.append(ram)

        # 16K to 32K
        if lo_rom == 1:
            new_map.append(ram)
        else:
            new_map.append('ROM')

        # 32K to 48K
        if mid_rom == 0:
            new_map.append('ROM')
        elif mid_rom == 1:
            new_map.append('FROM')
        elif mid_rom == 2:
            new_map.append('CROM')
        else:
            new_map.append(ram)

        # 48 to 52K
        if hi_rom == 0:
            new_map.append('ROM')
        elif hi_rom == 1:
            new_map.append('FROM')
        elif hi_rom == 2:
            new_map.append('CROM')
        else:
            if (common > 2) and (common_size == 3):
                new_map.append('RAM')
            else:
                new_map.append(ram)

        # 52K to 56K
        if io_on == 0:
            new_map.append('IO')
        elif hi_rom == 0:
            new_map.append('ROM')
        elif hi_rom == 1:
            new_map.append('FROM')
        elif hi_rom == 2:
            new_map.append('CROM')
        else:
            if (common > 2) and (common_size == 3):
                new_map.append('RAM')
            else:
                new_map.append(ram)

        # 56K to 60K
        if hi_rom == 0:
            new_map.append('ROM')
        elif hi_rom == 1:
            new_map.append('FROM')
        elif hi_rom == 2:
            new_map.append('CROM')
        else:
            if (common > 2) and (common_size > 1):
                new_map.append('RAM')
            else:
                new_map.append(ram)

        # 60K to 63K
        if hi_rom == 0:
            new_map.append('ROM')
        elif hi_rom == 1:
            new_map.append('FROM')
        elif hi_rom == 2:
            new_map.append('CROM')
        else:
            if (common > 2) and (common_size > 0):
                new_map.append('RAM')
            else:
                new_map.append(ram)

        # Always visible MMU registers
        new_map.append('IO')

        # 63K to 64K
        if hi_rom == 0:
            new_map.append('ROM')
        elif hi_rom == 1:
            new_map.append('FROM')
        elif hi_rom == 2:
            new_map.append('CROM')
        else:
            if common > 2:
                new_map.append('RAM')
            else:
                new_map.append(ram)
        return new_map

    def initC64(self):
        c64basic = config['C64']['basic']
        c64basic_start = 0xA000

        c64kernal = config['C64']['kernal']
        c64kernal_start = 0xE000

        c64character = config['C64']['character']
        c64character_start = 0xD000

        self.images['ROM'].load_binary(c64basic, c64basic_start)
        self.images['ROM'].load_binary(c64kernal, c64kernal_start)
        self.images['ROM'].load_binary(c64character, c64character_start)

        self.region_list = [(0x0000, 0x0002), (0x0002, 0x1000), (0x1000, 0x8000), (0x8000, 0xA000),
                            (0xA000, 0xC000), (0xC000, 0xD000), (0xD000, 0xE000), (0xE000, 0x10000)]

        self.mapping_table = [dict() for _ in range(0, len(self.region_list))]
        self.change_config(31)

    def initC128(self):
        self.images['RAM1'] = ProgramImage()
        self.images['RAM2'] = ProgramImage()
        self.images['RAM3'] = ProgramImage()
        self.images['FROM'] = ProgramImage()

        c128basic_lo = config['C128']['basiclo']
        c128basic_lo_start = 0x4000

        c128basic_hi = config['C128']['basichi']
        c128basic_hi_start = 0x8000

        c128kernal = config['C64']['kernal']
        c128kernal_start = 0xC000

        c128character = config['C64']['character']
        c128character_start = 0xD000

        self.images['ROM'].load_binary(c128basic_lo, c128basic_lo_start)
        self.images['ROM'].load_binary(c128basic_hi, c128basic_hi_start)
        self.images['ROM'].load_binary(c128kernal, c128kernal_start)
        self.images['ROM'].load_binary(c128character, c128character_start)

        self.region_list = [(0x0000, 0x0002), (0x0002, 0x0400), (0x0400, 0x1000), (0x1000, 0x2000),
                            (0x2000, 0x4000), (0x4000, 0x8000), (0x8000, 0xC000), (0xC000, 0xD000),
                            (0xE000, 0xF000), (0xF000, 0xFC00), (0xFC00, 0xFF00), (0xFF00, 0xFF05),
                            (0xFF05, 0x10000)]
        self.mapping_table = [dict() for _ in range(0, len(self.region_list))]
        self.change_config(0x400)

    def init1541(self):
        rom = config['1541']['rom']
        rom_start = 0xC000

        self.images['ROM'].load_binary(rom, rom_start)

        self.region_list = [(0x0000, 0x0800), (0x0800, 0x1800), (0x1800, 0x1810), (0x1810, 0x1C00),
                            (0x1C00, 0x1C10), (0x1C10, 0xC000), (0xC000, 0x10000)]
        self.mapping_table = [dict() for _ in range(0, len(self.region_list))]
        self.change_config(0)

    def init1571(self):
        rom = config['1571']['rom']
        rom_start = 0x8000

        self.images['ROM'].load_binary(rom, rom_start)

        self.region_list = [(0x0000, 0x0800), (0x0800, 0x1800), (0x1800, 0x1810), (0x1810, 0x1C00),
                            (0x1C00, 0x1C10), (0x1C10, 0x2000), (0x2000, 0x2004), (0x2004, 0x4000),
                            (0x4000, 0x4010), (0x4010, 0x8000), (0x8000, 0x10000)]
        self.mapping_table = [dict() for _ in range(0, len(self.region_list))]
        self.change_config(0)

    def init1581(self):
        rom = config['1581']['rom']
        rom_start = 0x8000

        self.images['ROM'].load_binary(rom, rom_start)

        self.region_list = [(0x0000, 0x2000), (0x2000, 0x4000), (0x4000, 0x8000), (0x8000, 0x10000)]
        self.mapping_table = [dict() for _ in range(0, len(self.region_list))]
        self.change_config(0)

    def initMappings(self, region_types: List[str]):
        region_num = len(self.region_list)
        self.mapping_table = [dict() for _ in range(0, region_num)]

        for i in range(0, region_num):
            start = self.region_list[i][0]
            end = self.region_list[i][1]
            for region_type in region_types:

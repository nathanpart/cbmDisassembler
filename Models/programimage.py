import struct

from Models.image_section import ImageSection


class ProgramImage:
    """
    Class that represents a 64K images. Tracks where loaded image files are.
    """
    program_image: bytearray
    sections: list

    def __init__(self):
        self.program_image = bytearray(64 * 1024)
        self.sections = list()

    def __len__(self):
        return len(self.program_image)

    def __getitem__(self, item):
        return self.program_image[item]

    def __setitem__(self, key, value):
        self.program_image[key] = value

    def __delitem__(self, key):
        del(self.program_image[key])

    def __contains__(self, item):
        return item in self.program_image

    def __iter__(self):
        return self.program_image.__iter__()

    def __reversed__(self):
        return self.program_image.__reversed__()

    def load_image(self, filename):
        """
        Loads an image file into the image. The first two bytes of the image file is the location where
        the file contents will be placed in the image.

        :param filename: Name of the file to load into the image
        :return: section info for the loaded filename, None if error occurred
        """
        with open(filename, 'rb') as f:
            the_file = f.read()

        address = struct.unpack_from('<H', the_file, 0)[0]
        image = the_file[2::]
        end_address = len(image) + address

        if self.is_collision(address, end_address):
            return None

        section = ImageSection(address, end_address, filename, 'PRG')
        self.program_image[address:end_address] = image
        self.sections.append(section)
        return section

    def load_binary(self, filename: str, base: int):
        """
        Loads an image file into the image. All bytes in the image are considered data and thus, the base address
        to load the data at is given as the second parameter.

        :param filename: name of the file load into the image
        :param base: address of where to load file at
        :return: section info for the loaded filename, None if error occurred
        """
        with open(filename, 'rb') as f:
            image = f.read()

        end_address = len(image) + base

        if self.is_collision(base, end_address):
            return None

        section = ImageSection(base, end_address, filename, 'BIN')
        self.program_image[base:end_address] = image
        self.sections.append(section)
        return section

    def define_section(self, address, size, name):
        end_address = address + size

        if self.is_collision(address, size):
            return None

        section = ImageSection(address, end_address, name, 'BSS')
        self.sections.append(section)
        return section

    def print_section_list(self):
        """
        Print the list of image sections
        """
        print('Images: ')
        for section in self.sections:
            print('start: {:04X}  end: {:04X}  {}'.format(section.start_address, section.end_address,
                                                          section.file_name))

    def get_section_list(self) -> list:
        """
        Returns a list of strings of the loaded images and their locations

        :return: List of loaded images
        """
        image_list = list()
        for section in self.sections:
            image_list.append('{:04X} - {:04X} {} {}'.format(section.start_address, section.end_address,
                                                             section.file_name, section.section_type))
        return image_list

    def in_loaded_image(self, address):
        for section in self.sections:
            if section.start_address <= address < section.end_address:
                return True
        return False

    def is_collision(self, start, end):
        for section in self.sections:
            if start <= section.start_address < end:
                return True
            elif start <= section.end_address < end:
                return True
            elif section.start_address <= start < section.end_address:
                return True
        return False

    def get_image_info(self, address):
        for section in self.sections:
            if section.start_address <= address < section.end_address:
                return section
        return None

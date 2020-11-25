
class ImageSection:
    start_address: int
    end_address: int
    file_name: str
    section_type: str

    def __init__(self, start, end, file_name, sec_type):
        self.start_address = start
        self.end_address = end
        self.file_name = file_name
        self.section_type = sec_type

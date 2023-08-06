from tempfile import NamedTemporaryFile

from qrcode import QRCode
from qrcode.constants import ERROR_CORRECT_H


class QRCodeClient:
    controller = None
    size = 0

    def __init__(self, size: int = 250, border: int = 2, *args, **kwargs):
        self.size = self.__verify_size(size)
        self.border = border
        self.init_controller()

    def init_controller(self):
        config = {
            "version": 1,
            "error_correction": ERROR_CORRECT_H,
        }
        config.update({"box_size": self.size // 25, "border": self.border})
        self.controller = QRCode(**config)

    def __verify_size(self, size):
        if self.size % 25 != 0:
            raise Exception("size 应为 25 的倍数")
        return size

    def make(self, content, path: str = None):
        self.controller.clear()
        self.controller.add_data(content)
        self.controller.make()
        img = self.controller.make_image()
        if path is None:
            img_file = NamedTemporaryFile()
            img.save(img_file)
            return img_file
        else:
            with open(path, "wb+") as img_file:
                img.save(img_file)
        return None

import sys
import os


class PictureSynthesis:
    """
        图片合成  图片a=100k file(b)=10M  new_file>10M
    """

    def __init__(self, img_file, other_file, new_file):
        self.old_img = img_file
        self.big_file = other_file
        self.new_img = new_file

    def picture_synthesis(self):
        os_name = sys.platform
        if os_name == 'linux' or os_name == 'darwin':
            os.system(f'cat {self.old_img} {self.big_file} >{self.new_img}')
        elif os_name == 'win32':
            os.system(f'copy /b {self.old_img}+{self.big_file} {self.new_img} ')
        else:
            print('此系统暂不支持')

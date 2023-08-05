import hashlib
import hmac

"""
@description: 加密方法
"""


class Encryption:
    def __init__(self, not_encrypted_str, mode, salt=''):
        """

        :param not_encrypted_str: 未加密字符串
        :param mode: 加密方式 md5、sha256...
        :param salt: 盐 可选
        """
        self.mode = mode  # Es = Encrypted string
        self.salt = salt
        self.NES = not_encrypted_str

    def encryption(self):
        if self.salt == '':
            encrypted_string = hashlib.new(self.mode, bytes(self.NES, encoding='utf-8')).hexdigest()
            return encrypted_string

        else:
            encrypted_string = hmac.new(
                bytes(self.salt, encoding='utf-8'), bytes(self.NES, encoding='utf-8'), self.mode
            )
            return encrypted_string.hexdigest()

        """
        Example 1

        esd = Encryption('123456', 'md5', 'salt').encryption()
        print(esd)

        Example 2
        esd = Encryption('123456', 'md5').encryption()
        """

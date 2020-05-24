from Crypto.Cipher import AES
import base64
from uuid import uuid4
import math


class AESCrypt:

    def __init__(self, key, model="ECB", iv="", encode_="utf-8"):
        """
        参数：
            key: 加密秘钥
            model： 加密模式
            iv： CBC模式下的iv
            encode: 编码
        """
        self.encode_ = encode_
        self.model = {'ECB': AES.MODE_ECB, 'CBC': AES.MODE_CBC}[model]
        self.key = self.add_16(key)
        if model == 'ECB':
            self.aes = AES.new(self.key, self.model)  # 创建一个aes对象
        elif model == 'CBC':
            self.aes = AES.new(self.key, self.model, iv)  # 创建一个aes对象

        # 这里的密钥长度必须是16、24或32，目前16位的就够用了

    def add_16(self, par):
        par = par.encode(self.encode_)
        while len(par) % 16 != 0:
            par += b'\x00'
        return par

    def aesencrypt(self, text):
        text = self.add_16(text)
        self.encrypt_text = self.aes.encrypt(text)
        return base64.encodebytes(self.encrypt_text).decode().strip()

    def aesdecrypt(self, text):
        text = base64.decodebytes(text.encode(self.encode_))
        self.decrypt_text = self.aes.decrypt(text)
        return self.decrypt_text.decode(self.encode_).strip('\0')
    """
    if __name__ == '__main__':
        pr = aescrypt('12345','ECB','','gbk')
        en_text = pr.aesencrypt('好好学习')
        print('密文:',en_text)
        print('明文:',pr.aesdecrypt(en_text))
    """


uuidChars = ("a", "b", "c", "d", "e", "f",
             "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s",
             "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5",
             "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I",
             "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
             "W", "X", "Y", "Z")


def short_uuid(uuid_len=8):
    """
    生成指定长度的uuid，默认长度为8,为了保证uuid 有效，长度必须大于等于8
    本算法利用62个可打印字符，通过随机生成32位UUID，由于UUID都为十六进制，所以将UUID分成8组，每4个为一组，然后通过模62操作，结果作为索引取出字符，
    最后生成的Uuid，只有8位，    
    """
    uuid_len = 8 if uuid_len < 8 else uuid_len  # 小于8 也生成大于8的长度
    uuid_str_len = uuid_len * 4 + 4
    need_create_uuid_num = math.ceil(uuid_str_len / 36)
    uuid_str = "".join([str(uuid4()) for i in range(need_create_uuid_num)])
    uuid_str = uuid_str.replace("-", "")
    result = ''
    for i in range(0, uuid_len):
        sub = uuid_str[i * 4: i * 4 + 4]
        x = int(sub, 16)
        result += uuidChars[x % 0x3E]
    return result

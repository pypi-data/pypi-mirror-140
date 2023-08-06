from pprint import pformat
from secrets import token_hex
from typing import NamedTuple

# poetry add pycryptodomex
from Cryptodome.Cipher import AES


class SecretDataAes(NamedTuple):
    """
    Структура для хранения секретных данных
    """
    #: Нужен для дешифровки (Ключ)
    nonce: bytes
    #: Зашифрованные данные
    ciphertext: bytes
    #: Проверка подлинности
    tag: bytes

    def toDict(self):
        return self._asdict()


class CryptoAes:
    """
    Шифрование текста алгоритмом ``AES``

    `Документация AES
    <https://pycryptodome.readthedocs.io/en/latest/src/cipher/aes.html>`_

    :Пример:

    .. code-block:: python

        A = CryptoAes(key="Sixteen byte kys")
        secret_data: SecretDataAes = A.encodeAES("Мои секретные данные")
        ###################
        B = CryptoAes(key="Sixteen byte kys")
        print(B.decodeAES(secret_data))
        # Мои секретные данные
    """
    __slots__ = ["__key"]

    def __init__(self, key: str):
        """
        :param key: Ключ для шифрования, должен иметь длину 16,24,32 байта
        """
        #: Ключ для шифрования, должен иметь длину 16,24,32 байта
        self.__key: bytes = self.check_len_password(key.encode('utf-8'))

    def encodeAES(self, text: str) -> SecretDataAes:
        """
        Закодировать данные
        """
        cipher = AES.new(self.__key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(text.encode("utf-8"))
        return SecretDataAes(nonce=nonce, ciphertext=ciphertext, tag=tag)

    def decodeAES(self, secret_data: SecretDataAes) -> str:
        """
        Раскодировать данные

        :param secret_data:
        """
        cipher = AES.new(self.__key, AES.MODE_EAX, nonce=secret_data.nonce)
        try:
            plaintext = cipher.decrypt_and_verify(secret_data.ciphertext, secret_data.tag)
            return plaintext.decode("utf-8")
        except ValueError:
            raise ValueError("Не удалось расшифровать данные")

    def __str__(self):
        return pformat(self.__dict__)

    ##############################################################
    @staticmethod
    def generate_password(len_: int = 16):
        """
        Создать случайный пароль необходимой длинны пароль
        """
        return token_hex(len_)

    @staticmethod
    def check_len_password(key: bytes) -> bytes:
        """
        Проверить длину пароля
        """
        if len(key) in (16, 24, 32):
            return key
        else:
            raise ValueError("Длинна ключа должна быть 16,24,32 байта")

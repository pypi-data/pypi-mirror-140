# -*- coding:utf-8 -*-
from typing import Dict, Union
from .utils import cleaning


class BaseCpfCnpj:
    def __init__(self, document: str) -> None:
        """
        Class to interact with cpf and cnpj brazilian numbers
        """
        self._document = document

    def validate(self):
        raise NotImplementedError

    def format(self):
        """
        Method to format cnpj numbers.
        """
        raise NotImplementedError

    def cleaning(self) -> str:
        """Returns document without special chars

        Returns
            str: CPF or CNPJ cleaned
        """
        return cleaning(self._document)

    @property
    def document(self):
        return self._document


class Cnpj(BaseCpfCnpj):

    @staticmethod
    def _calculating_digit(result):
        result = result % 11
        if result < 2:
            digit = 0
        else:
            digit = 11 - result
        return str(digit)

    def _calculating_first_digit(self):
        one_validation_list = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        result = 0
        pos = 0
        for number in self.cleaning():
            try:
                one_validation_list[pos]
            except IndexError:
                break
            result += int(number) * int(one_validation_list[pos])
            pos += 1
        return self._calculating_digit(result)

    def _calculating_second_digit(self):
        two_validation_list = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        result = 0
        pos = 0
        for number in self.cleaning():
            try:
                two_validation_list[pos]
            except IndexError:
                break
            result += int(number) * int(two_validation_list[pos])
            pos += 1
        return self._calculating_digit(result)

    def validate(self):
        document = self.cleaning()

        if len(document) != 14:
            return False

        checkers = document[-2:]

        digit_one = self._calculating_first_digit()
        digit_two = self._calculating_second_digit()

        return bool(checkers == digit_one + digit_two)

    def format(self):
        """
        Method to format cnpj numbers.
        """
        return '%s.%s.%s/%s-%s' % (
            self.document[0:2], self.document[2:5],
            self.document[5:8], self.document[8:12],
            self.document[12:14])


class Cpf(BaseCpfCnpj):

    def _validate_size(self):
        cpf = self.cleaning()
        if len(cpf) > 11 or len(cpf) < 11:
            return False
        return True

    def validate(self):
        if self._validate_size():
            digit_1 = 0
            digit_2 = 0
            i = 0
            cpf = self.cleaning()
            while i < 10:
                digit_1 = ((digit_1 + (int(cpf[i]) * (11-i-1))) % 11
                    if i < 9 else digit_1)
                digit_2 = (digit_2 + (int(cpf[i]) * (11-i))) % 11
                i += 1
            return ((int(cpf[9]) == (11 - digit_1 if digit_1 > 1 else 0)) and
                    (int(cpf[10]) == (11 - digit_2 if digit_2 > 1 else 0)))
        return False

    def format(self):
        return '%s.%s.%s-%s' % (self.document[0:3],
                                self.document[3:6],
                                self.document[6:9],
                                self.document[9:11])
    

class CpfCnpj:
    
    _validators: Dict[str, Union[Cpf, Cnpj]] = {
        "cpf": Cpf,
        "cnpj": Cnpj
    }

    @classmethod
    def _cleaning(cls, document: str) -> str:
        return document.replace('-', '').replace('.', '').replace('/', '')

    @classmethod
    def factory(cls, document: str) -> Union[Cpf, Cnpj]:
        doc = cls._validators['cpf']
        if len(cls._cleaning(document)) > 11:
            doc = cls._validators['cnpj']
        return doc(document) # noqa


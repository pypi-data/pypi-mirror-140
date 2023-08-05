# -*- coding:utf-8 -*-

import os
from setuptools import setup, find_packages

setup(
    install_requires=["coverage",
                      "nose"],
    name="validate_cpf_cnpj",
    version='0.1.2',
    description="Validador de CPF e CNPJ para Python",
    license="MIT",
    author="El Cidon",
    author_email="erickfabiani123@gmail.com",
    url="https://github.com/elcidon/cpf_cnpj",
    packages=find_packages(exclude=['tests']),
    keywords="python cpf cnpj validador",
    zip_safe=True
)

CPF e CNPJ
==========

Validador de CPF e CNPJ.

**Install**


``` python

  pip install cpf_cnpj
```

**Usage**

``` python

  from cpf_cnpj import Cpf, Cnpj
  
  cpf = Cpf('85725262502')

  cpf.format()
  '857.252.625-02'
  
  cpf.cleaning()
  '85725262502'
  
  cpf.validate()
  True
  
  cnpj = Cnpj('97373439000100')

  cnpj.format()
  '97.373.439/0001-00'
  
  cnpj.cleaning()
  '97373439000100'
  
  cnpj.validate()
  True]
```

## You can use just one class to validate a CPF or CNPJ

usage:
```python
from cpf_cnpj import CpfCnpj

# CNPJ
document = CpfCnpj.factory("95.448.834/0001-70")

document.validate()
True

document.cleaning()
'95448834000170'

document = CpfCnpj.factory("95448834000170")

document.format()
'95.448.834/0001-70'

#CPF
document = CpfCnpj.factory("335.101.310-88")

document.validate()
True

document.cleaning()
'33510131088'

document = CpfCnpj.factory("33510131088")

document.format()
'335.101.310-88'

```

**Tests**

``` python

  cd cpf_cnpj/tests

  ./run_tests.sh
```

# package_viacep

Description. 
The package package_viacep is used to:
	- Utility for Brazil zip code query
	- Utility for Brazil zip code validation

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install package_viacep

```bash
pip install package_viacep
```

## Usage

```python
from package_viacep import viacep
instance = viacep.ViaCep()
''' Return of Dict Object'''
data = instance.GetData('Zip Code')
```

## Author
Antonio Oliveira

## License
[MIT](https://choosealicense.com/licenses/mit/)
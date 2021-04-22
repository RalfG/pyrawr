# pyrawr

[![](https://flat.badgen.net/pypi/v/pyrawr?icon=pypi)](https://pypi.org/project/pyrawr)
[![](https://flat.badgen.net/github/release/ralfg/pyrawr)](https://github.com/ralfg/pyrawr/releases)
[![](https://flat.badgen.net/github/checks/ralfg/pyrawr/)](https://github.com/ralfg/pyrawr/actions)
![](https://flat.badgen.net/github/last-commit/ralfg/pyrawr)
![](https://flat.badgen.net/github/license/ralfg/pyrawr)


Python wrapper around the
[ThermoRawFileParser](https://github.com/compomics/ThermoRawFileParser)
command line interface.

This Python module uses the ThermoRawFileParser CLI to retrieve general run metadata, specific spectra, or specific XICs, directly as Python lists and dictionaries from
mass spectrometry raw files. Parsing raw files to other file formats is also supported.


---


## Installation

- Install pyrawr with pip

   ```sh
   $ pip install pyrawr
   ```

- Install [ThermoRawFileParser](https://github.com/compomics/ThermoRawFileParser) or
Docker.

For Docker, the current user must be
[added to the Docker group](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user),
that is, be callable as `docker run`, instead of `sudo docker run`.


## Usage

See
[full API documentation](https://pyrawr.readthedocs.io/en/latest/api.html)
for all pyrawr functionality.


Parse raw file to any supported output format:

```python
>>> from pyrawr import ThermoRawFileParser
>>> trfp = ThermoRawFileParser(
...     executable="thermorawfileparser",
...     docker_image="quay.io/biocontainers/thermorawfileparser:1.3.3--ha8f3691_1"
... )
>>> trfp.parse("OR4_110719_OB_PAR14_sSCX_fr10.raw", output_format="mzml")
```


Get raw file metadata:

```python
>>> trfp.metadata("OR4_110719_OB_PAR14_sSCX_fr10.raw")
{'FileProperties': [{'accession': 'NCIT:C47922', 'cvLabel': 'NCIT' ... }]}
```


Query a specific spectrum:

```python
>>> trfp.query("OR4_110719_OB_PAR14_sSCX_fr10.raw", "508,680")
[{'mzs': [204.8467254638672,
   262.4529113769531,
   309.53961181640625,
   ...
```


Retrieve one or more chromatograms based on a query:

```python
>>> trfp.xic(
...     "OR4_110719_OB_PAR14_sSCX_fr10.raw",
...     [{"mz":488.5384, "tolerance":10, "tolerance_unit":"ppm"}],
... )
{'OutputMeta': {'base64': False, 'timeunit': 'minutes'},
 'Content': [{'Meta': {'MzStart': 488.53351461600005,
    'MzEnd': 488.543285384,
    'RtStart': 0.007536666666666666,
    'RtEnd': 179.99577166666666},
   'RetentionTimes': [0.007536666666666666,
    0.022771666666666666,
    0.036936666666666666,
    ...
```

## Contributing

Bugs, questions or suggestions? Feel free to post an issue in the
[issue tracker](https://github.com/RalfG/pyrawr/issues/) or to make a pull
request! See
[Contributing.md](https://pyrawr.readthedocs.io/en/latest/contributing.html)
for more info.

This module currently uses Python's `subprocess.run()` to access ThermoRawFileParser.
There are probably much better methods that would directly access the
ThermoRawFileParser library, circumventing the CLI. Suggestions and PRs are always
welcome.


## Changelog

See [Changelog](https://pyrawr.readthedocs.io/en/latest/changelog.html).

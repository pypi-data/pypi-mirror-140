# fdtdempy
## _FDTD Electromagnetic Field Simulator_

fdtdempy is a Python implemented FDTD Electromagnetic Field Simulator. It is implemented in Cython to optimize performance and can be configured using Python.

## Features

- Simulates the effect of an alternating current source on the surrounding electric and magnetic field
- Fast performance due to Cython implementation
- Fully configurable and extendable

## Installation

fdtdempy requires Python 3 to run. Use pip to install the library

```sh
pip install fdtdempy
```

## Building from source

To build the Cython code run the following command in the root of the project

```sh
python setup.py build_ext --inplace
```
If you get the following error

```sh
error: Unable to find vcvarsall.bat
```

you need to install the Visual Studio 2019 Worlkload Tools using the command

```sh
choco install visualstudio2019-workload-vctools
```

Once the .pyd files have been built you need to remove the previous .pyd files and rename the new files to the old names, eg core.cp39-win_amd64.pyd must be renamed to core.pyd

## Using the library

The file example.py implements an example of using the simulator to simulate a dipole antenna. 

## License

MIT


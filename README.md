# PySTM32.AI

A python wrapper for the `stedgeai` command-line tool to analyse deep learning models for STM32 microcontrollers.

Disclaimer: This project is not related to STMicroelecronics, it is as a wrapper around a component of [X-CUBE-AI](https://www.st.com/en/embedded-software/x-cube-ai.html) property of STMicroelecronics and licensed under SLA (see more below).

Limitations: Currently this project works only on linux.

## How it works

The API provide two functions : `analyse` and `generate`, the first one gives information about the size of a model and the second one can be used to generate C files to link with X-CUBE-AI runtime library (Not provided in this package).

The package doesn't include stm32ai executable so it will download and install it automatically on first call.

A command line utility is also provided (`pystm32ai`), however it currently doesn't match the full functionality provided by the original `stm32ai` executable.

## Installation

With pip:

```bash
pip install pystm32ai
```

## Usage

### Python API

The goal of this tool is to use stm32ai in a deep learning training pipeline, where it can give information about the final model running on STM32

```python
from pystm32ai import stm32ai

report = stm32ai.analyse('path/to/model.tflite')
print(report)

stm32ai.generate('path/to/model.tflite') # C files are generated in the current directory
```

### Command line tool

The project can also be used as a command line tool:

```sh
pystm32ai analyse path/to/model.tflite
pystm32ai generate path/to/model.tflite
```

Here is the full usage :

```text
usage: pystm32ai [-h] [--allocate-inputs] [--allocate-outputs] [--full-report] [--output_dir OUTPUT_DIR] [--name NAME] {analyse,generate} model_path

Python wrapper around stm32ai command line tool

positional arguments:
  {analyse,generate}    Action to run on stm32ai
  model_path            Path to model

optional arguments:
  -h, --help            show this help message and exit
  --allocate-inputs
  --allocate-outputs
  --full-report
  --output_dir OUTPUT_DIR
  --name NAME           Name of the model
```

### Full API specification

```python
def analyse(
    model_path, allocate_inputs=True, allocate_outputs=False, full_report=False
):
    """
    Analyse a model with CubeAI to get info about RAM, ROM and MACC
    Params:
        model_path: path to a model (ONNX, h5 or TFLITE)
        allocate_inputs: whether to allocate input tensor with activations
        allocate_outputs: whether to allocate output tensor with activations
        full_report: Get a full report with per-layers information
    Returns:
        A report as a dictionary
    """

def generate(
    model_path, allocate_inputs=True, allocate_outputs=False, name=None, output_dir="."
):
    """
    Generate a model C files to use in a STM32 application
    Params:
        model_path: path to a model (ONNX, h5 or TFLITE)
        allocate_inputs: whether to allocate input tensor with activations
        allocate_outputs: whether to allocate output tensor with activations
        output_dir: Path to output directory (default current working directory)
    """
```

## License

The pystm32ai project is under the [MIT License](https://spdx.org/licenses/MIT.html)

It's using part of the X-CUBE-AI software which is under SLA0104 license, hence, by using this software you agree to the terms and condition of this license.

X-CUBE-AI in turn is using many licensed software, here's a summarized list of licenses used by X-CUBE-AI software components:

- SLA (STMicroelectronics License Agreement)
    - STM32Cube.AI tools and libraries
    - STM32N6xx_HAL_Driver
    - BSP components
- Apache-2.0
    - CMSIS (Arm)
    - TensorFlow related components
    - Google components (flatbuffers, auth, pasta)
    - Various ML tools (absl, gemmlowp, ruy)
- BSD-3-Clause
    - AI runner and examples
    - numpy
    - scipy
    - scikit-learn
    - h5py
    - protobuf
- MIT
    - Many Python utilities (attrs, charset_normalizer, urllib3, wrapt)
    - Various parsers and tools (jsonschema, mako, onnx)
    - UI/formatting tools (termcolor, terminaltables, tqdm)
- Python-2.0
    - Python core
    - astunparse
    - typing_extensions
- LGPL-2.1
    - astroid
    - chardet
- MPL-2.0 (certifi)
- GPLv2 (xdis)
- GPLv3 (uncompyle6)
- BSD-2-Clause (pycryptodome, pygments)
- The Unlicense (pyelftools)

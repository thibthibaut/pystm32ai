# PySTM32.AI

A python wrapper for the `stm32ai` command-line tool to analyse deep learning models for STM32 microcontrollers.

Disclaimer: This project is not related to STMicroelecronics, it is as a wrapper around a component of [X-CUBE-AI](https://www.st.com/en/embedded-software/x-cube-ai.html) property of STMicroelecronics and licensed under SLA0048 (see more below).

## How it works

The API provide two functions : `analyse` and `generate`, the first one gives information about the size of a model and the second one can be used to generate C files to link with X-CUBE-AI runtime library (Not provided in this package).

The package doesn't include stm32ai executable so it will download and install it automatically on first call.

A command line utility is also provided (`pystm32ai`), however it currently doesn't match the full functionality provided by the original `stm32ai` executable.

## Installation

With pip:

```bash
pip3 install pystm32ai
```

From wheel:

Download wheel from Releases and install with pip:

```bash
pip3 install pystm32ai-*.whl
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

It's using part of the X-CUBE-AI software which is under SLA0048 license, hence, by using this software you agree to the terms and condition of the SLA048 license. A copy of the license for X-CUBE-AI is provided below:

```text
SLA0048 Rev4/March 2018

BY INSTALLING COPYING, DOWNLOADING, ACCESSING OR OTHERWISE USING THIS SOFTWARE PACKAGE OR ANY PART THEREOF (AND THE RELATED DOCUMENTATION) FROM STMICROELECTRONICS INTERNATIONAL N.V, SWISS BRANCH AND/OR ITS AFFILIATED COMPANIES (STMICROELECTRONICS), THE RECIPIENT, ON BEHALF OF HIMSELF OR HERSELF, OR ON BEHALF OF ANY ENTITY BY WHICH SUCH RECIPIENT IS EMPLOYED AND/OR ENGAGED AGREES TO BE BOUND BY THIS SOFTWARE PACKAGE LICENSE AGREEMENT.

Under STMicroelectronics’ intellectual property rights and subject to applicable licensing terms for any third-party software incorporated in this software package and applicable Open Source Terms (as defined here below), the redistribution, reproduction and use in source and binary forms of the software package or any part thereof, with or without modification, are permitted provided that the following conditions are met:
1. Redistribution of source code (modified or not) must retain any copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form, except as embedded into microcontroller or microprocessor device manufactured by or for STMicroelectronics or a software update for such device, must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of STMicroelectronics nor the names of other contributors to this software package may be used to endorse or promote products derived from this software package or part thereof without specific written permission.
4. This software package or any part thereof, including modifications and/or derivative works of this software package, must be used and execute solely and exclusively on or in combination with a microcontroller or a microprocessor devices manufactured by or for STMicroelectronics.
5. No use, reproduction or redistribution of this software package partially or totally may be done in any manner that would subject this software package to any Open Source Terms (as defined below).
6. Some portion of the software package may contain software subject to Open Source Terms (as defined below) applicable for each such portion (“Open Source Software”), as further specified in the software package. Such Open Source Software is supplied under the applicable Open Source Terms and is not subject to the terms and conditions of license hereunder. “Open Source Terms” shall mean any open source license which requires as part of distribution of software that the source code of such software is distributed therewith or otherwise made available, or open source license that substantially complies with the Open Source definition specified at www.opensource.org and any other comparable open source license such as for example GNU General Public License (GPL), Eclipse Public License (EPL), Apache Software License, BSD license and MIT license.
7. This software package may also include third party software as expressly specified in the software package subject to specific license terms from such third parties. Such third party software is supplied under such specific license terms and is not subject to the terms and conditions of license hereunder. By installing copying, downloading, accessing or otherwise using this software package, the recipient agrees to be bound by such license terms with regard to such third party software.
8. STMicroelectronics has no obligation to provide any maintenance, support or updates for the software package.
9. The software package is and will remain the exclusive property of STMicroelectronics and its licensors. The recipient will not take any action that jeopardizes STMicroelectronics and its licensors' proprietary rights or acquire any rights in the software package, except the limited rights specified hereunder.
10. The recipient shall comply with all applicable laws and regulations affecting the use of the software package or any part thereof including any applicable export control law or regulation.
11. Redistribution and use of this software package partially or any part thereof other than as permitted under this license is void and will automatically terminate your rights under this license.

THIS SOFTWARE PACKAGE IS PROVIDED BY STMICROELECTRONICS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS, IMPLIED OR STATUTORY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY INTELLECTUAL PROPERTY RIGHTS ARE DISCLAIMED TO THE FULLEST EXTENT PERMITTED BY LAW. IN NO EVENT SHALL STMICROELECTRONICS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE PACKAGE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
EXCEPT AS EXPRESSLY PERMITTED HEREUNDER AND SUBJECT TO THE APPLICABLE LICENSING TERMS FOR ANY THIRD-PARTY SOFTWARE INCORPORATED IN THE SOFTWARE PACKAGE AND OPEN SOURCE TERMS AS APPLICABLE, NO LICENSE OR OTHER RIGHTS, WHETHER EXPRESS OR IMPLIED, ARE GRANTED UNDER ANY PATENT OR OTHER INTELLECTUAL PROPERTY RIGHTS OF STMICROELECTRONICS OR ANY THIRD PARTY.
```

The X-CUBE-AI is in turn using licensed components, for more info about these check out [this pdf](https://www.st.com/resource/en/data_brief/x-cube-ai.pdf)

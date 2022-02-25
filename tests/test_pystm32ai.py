"""
SPDX-License-Identifier: MIT
stm32ai module
Wrapper around stm32ai executable
"""
import os
import tempfile
from src.pystm32ai import __version__
from src.pystm32ai.stm32ai import analyse
from src.pystm32ai.stm32ai import generate

DIR_PATH = os.path.dirname(__file__)


def test_version():
    assert __version__ == "0.1.0"


def test_analyse_model():
    report = analyse(os.path.join(DIR_PATH, "model_quant.tflite"))
    assert report["model_size"] == 220884
    assert report["rom_n_macc"] == 13421668


def test_generate_model():
    with tempfile.TemporaryDirectory() as tmp_dir:
        generate(os.path.join(DIR_PATH, "model_quant.tflite"), output_dir=tmp_dir)
        assert os.path.exists(os.path.join(tmp_dir, "network.c"))
        assert os.path.exists(os.path.join(tmp_dir, "network_data.c"))


def test_generate_dll():
    with tempfile.TemporaryDirectory() as tmp_dir:
        generate(
            os.path.join(DIR_PATH, "model_quant.tflite"), output_dir=tmp_dir, dll=True
        )
        assert os.path.exists(os.path.join(tmp_dir, "libai_network.so"))


def test_generate_dll_with_name():
    with tempfile.TemporaryDirectory() as tmp_dir:
        generate(
            os.path.join(DIR_PATH, "model_quant.tflite"),
            output_dir=tmp_dir,
            name="bobby",
            dll=True,
        )
        assert os.path.exists(os.path.join(tmp_dir, "libai_bobby.so"))

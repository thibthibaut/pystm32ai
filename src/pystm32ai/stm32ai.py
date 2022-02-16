"""
SPDX-License-Identifier: MIT
Copyright 2022 - Thibaut Vercueil

stm32ai module
Wrapper around stm32ai executable
"""
import tempfile
import subprocess
import json
import os
import stat
import platform
import argparse
from zipfile import ZipFile
import requests
from tqdm import tqdm

STM32AI_VERSION = "7.1.0"
PLATFORM = platform.system().lower()
if PLATFORM == "darwin":
    PLATFORM = "mac"

DIR_PATH = os.path.dirname(__file__)
EXE_NAME = "stm32ai.exe" if PLATFORM == "windows" else "stm32ai"
EXE_PATH = os.path.join(DIR_PATH, "exe", STM32AI_VERSION, PLATFORM, EXE_NAME)
EXE_URL = (
    f"https://sw-center.st.com/packs/x-cube-ai/stm32ai-{PLATFORM}-{STM32AI_VERSION}.zip"
)


def analyse(
    model_path, allocate_inputs=True, allocate_outputs=False, full_report=False
):
    """
    Analyse a model with CubeAI to get info about RAM, ROM and MACC
    Args:
        model_path: path to a model (ONNX, h5 or TFLITE)
        allocate_inputs: whether to allocate input tensor with activations
        allocate_outputs: whether to allocate output tensor with activations
        full_report: Get a full report with per-layers information
    Returns:
        A report as a dictionary
    """
    _check_and_download_executable()

    io_options = []
    if allocate_inputs:
        io_options.append("--allocate-inputs")
    if allocate_outputs:
        io_options.append("--allocate-outputs")

    with tempfile.TemporaryDirectory() as tmp_dir:
        subprocess.run(
            [
                EXE_PATH,
                "analyse",
                "-m",
                model_path,
                "-o",
                tmp_dir,
                "-w",
                tmp_dir,
                "-v",
                "0",
            ]
            + io_options,
            check=True,
        )
        report_path = os.path.join(tmp_dir, "network_report.json")
        with open(report_path, "r", encoding="utf-8") as file:
            report = json.load(file)

    if full_report:
        return report

    return {
        key: report[key]
        for key in [
            "rom_size",
            "rom_n_macc",
            "ram_size",
            "ram_io_size",
            "model_size",
        ]
    }


def generate(
    model_path, allocate_inputs=True, allocate_outputs=False, name=None, output_dir="."
):
    """
    Generate a model C files to use in a STM32 application
    Args:
        model_path: path to a model (ONNX, h5 or TFLITE)
        allocate_inputs: whether to allocate input tensor with activations
        allocate_outputs: whether to allocate output tensor with activations
        output_dir: Path to output directory (defualt current working directory)
    """
    _check_and_download_executable()
    io_options = []
    if allocate_inputs:
        io_options.append("--allocate-inputs")
    if allocate_outputs:
        io_options.append("--allocate-outputs")
    if name:
        io_options.append("--name")
        io_options.append("".join(name.split()))

    with tempfile.TemporaryDirectory() as tmp_dir:
        subprocess.run(
            [
                EXE_PATH,
                "generate",
                "-m",
                model_path,
                "-o",
                output_dir,
                "-w",
                tmp_dir,
                "-v",
                "0",
            ]
            + io_options,
            check=True,
        )


def run():
    """
    Run function to be called from command line usage
    """
    parser = argparse.ArgumentParser(
        description="Python wrapper around stm32ai command line tool"
    )
    parser.add_argument(
        "action", choices=["analyse", "generate"], help="Action to run on stm32ai"
    )
    parser.add_argument("model_path", help="Path to model")
    parser.add_argument("--allocate-inputs", action="store_true", default=True)
    parser.add_argument("--allocate-outputs", action="store_true", default=False)
    parser.add_argument("--full-report", action="store_true")
    parser.add_argument("--output_dir", default=".")
    parser.add_argument("--name", default=None, help="Name of the model")
    args = vars(parser.parse_args())

    action = args.pop("action")
    if action == "analyse":
        args.pop("output_dir")
        args.pop("name")
        model_report = analyse(**args)
        print(json.dumps(model_report, indent=4))
    if action == "generate":
        args.pop("full_report")
        print("Generating C files for model...")
        generate(**args)
        print("Done.")


def _check_and_download_executable():
    """
    Checks for the stm32ai exectuable and downloads it if it doesn't exist
    """
    if os.path.exists(EXE_PATH):
        return
    print("Didn't find stm32ai executable, downloading it")
    # Create a directory with cubeAI version under exe directory
    try:
        os.mkdir(os.path.join(DIR_PATH, "exe", STM32AI_VERSION))
    except OSError:
        ...

    # Download the file in a temporary directory and unzip it
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, "stm32ai.zip")
        _download(EXE_URL, zip_path)
        _unzip(zip_path, os.path.join(DIR_PATH, "exe", STM32AI_VERSION))

    os.chmod(EXE_PATH, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)


def _download(url, fname):
    """
    Utility function to download a file
    Args:
        url: URL of the file to be downloaded
        fname: Path of the file to be downloaded
    """
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get("content-length", 0))
    with open(fname, "wb") as file, tqdm(
        desc=fname,
        total=total,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as tqbar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            tqbar.update(size)


def _unzip(fname, directory):
    """
    Utility function to unzip a file
    Args:
        fname: Name of the file to be unzipped
        directory: Directory to unzip
    """
    with ZipFile(file=fname) as zip_file:
        for file in tqdm(
            desc="Unzipping",
            iterable=zip_file.namelist(),
            total=len(zip_file.namelist()),
        ):
            zip_file.extract(member=file, path=directory)


if __name__ == "__main__":
    run()

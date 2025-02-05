"""
SPDX-License-Identifier: MIT
Copyright 2022 - Thibaut Vercueil

stedgeai module
Wrapper around stedgeai executable
"""

from pathlib import Path
from rich.console import Console
from rich.table import Table
from tqdm import tqdm
from zipfile import ZipFile
import argparse
import inspect
import json
import os
import platform
import py7zr
import requests
import rich
import shutil
import subprocess
import tempfile

console = Console()

STEDGEAI_VERSION = "2.0"
PLATFORM = platform.system().lower()
if PLATFORM == "darwin":
    PLATFORM = "mac"

DIR_PATH = Path(__file__).parent
ASSET_PATH = DIR_PATH / "assets"
EXE_NAME = "stedgeai.exe" if PLATFORM == "windows" else "stedgeai"
EXE_PATH = (
    DIR_PATH
    / "assets"
    / "stedgeai"
    / STEDGEAI_VERSION
    / "Utilities"
    / PLATFORM
    / EXE_NAME
)
DLL_EXT = "dll" if PLATFORM == "windows" else "so"
REL_URL = "https://github.com/thibthibaut/pystm32ai/releases/download/v0.2.1"

def analyse(
    model_path,
    allocate_inputs=True,
    allocate_outputs=True,
    full_report=False,
    optimization="balanced",
    compression="lossless",
):
    """
    Analyse a model with CubeAI to get info about RAM, ROM and MACC
    Args:
        model_path: path to a model (ONNX, h5 or TFLITE)
        allocate_inputs: whether to allocate input tensor with activations
        allocate_outputs: whether to allocate output tensor with activations
        full_report: Get a full report with per-layers information
        optimization: Optimization strategy, can be none|lossless|low|medium|high
        compression: Compression level, can be time|ram|balanced
    Returns:
        A report as a dictionary
    """
    _check_and_download_executable()

    io_options = []
    if not allocate_inputs:
        io_options.append("--no-inputs-allocation")
    if not allocate_outputs:
        io_options.append("--no-outputs-allocation")

    with tempfile.TemporaryDirectory() as tmp_dir:
        with console.status("[blue]Analyzing model... Please wait...", spinner="dots"):
            subprocess.run(
                [
                    EXE_PATH,
                    "analyse",
                    "--target",
                    "stm32",
                    "--optimization",
                    optimization,
                    "--compression",
                    compression,
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
    model_path,
    allocate_inputs=True,
    allocate_outputs=True,
    optimization="balanced",
    compression="lossless",
    name=None,
    output_dir=".",
    dll=False,
):
    """
    Generate a model C files to use in a STM32 application
    Args:
        model_path: path to a model (ONNX, h5 or TFLITE)
        allocate_inputs: whether to allocate input tensor with activations
        allocate_outputs: whether to allocate output tensor with activations
        output_dir: Path to output directory (default current working directory)
        dll: Generate dynamic library to use the model on host
    """
    _check_and_download_executable()
    io_options = []
    if not allocate_inputs:
        io_options.append("--no-inputs-allocation")
    if not allocate_outputs:
        io_options.append("--no-outputs-allocation")
    if name:
        io_options.append("--name")
        name = "".join(name.split()).replace("-", "_")
        io_options.append(name)
    if dll:
        io_options.append("--dll")

    with tempfile.TemporaryDirectory() as tmp_dir:
        with console.status(
            "[yellow]Generating model files... Please wait...", spinner="dots"
        ):
            subprocess.run(
                [
                    EXE_PATH,
                    "generate",
                    "--target",
                    "stm32",
                    "--optimization",
                    optimization,
                    "--compression",
                    compression,
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
        if dll:
            net_name = "network" if name is None else name
            dll_name = f"libai_{net_name}.{DLL_EXT}"
            shutil.copyfile(
                os.path.join(
                    tmp_dir,
                    f"inspector_{net_name}",
                    "workspace",
                    "lib",
                    dll_name,
                ),
                os.path.join(output_dir, dll_name),
            )


def bytes_to_kib(bytes_value):
    """
    Converts bytes to KiB
    Args:
        bytes_value: value in bytes
    """
    return f"{bytes_value / 1024:.2f} KiB"


def run():
    """
    Run function to be called from command line usage
    """
    parser = argparse.ArgumentParser(
        description="Python wrapper around stedgeai command line tool"
    )
    parser.add_argument(
        "action", choices=["analyse", "generate"], help="Action to run on stedgeai"
    )
    parser.add_argument("model_path", help="Path to model")
    parser.add_argument(
        "--compression",
        choices=["none", "lossless", "low", "medium", "high"],
        help="Optimization strategy",
        default="lossless",
    )
    parser.add_argument(
        "--optimization",
        choices=["time", "ram", "balanced"],
        help="Optimization strategy",
        default="balanced",
    )
    parser.add_argument("--allocate-inputs", action="store_true", default=True)
    parser.add_argument("--allocate-outputs", action="store_true", default=True)
    parser.add_argument("--full-report", action="store_true")
    parser.add_argument("--output_dir", default=".")
    parser.add_argument("--name", default=None, help="Name of the model")

    args = vars(parser.parse_args())

    action = args.pop("action")
    if action == "analyse":
        args.pop("output_dir")
        args.pop("name")
        model_report = analyse(**args)
        if args.get("full_report"):
            rich.print(json.dumps(model_report, indent=4))
        else:
            report_table = Table(title="Model Analysis Report", show_lines=True)
            report_table.add_column("Metric", style="cyan", justify="left")
            report_table.add_column("Value (Bytes)", style="magenta", justify="right")
            report_table.add_column("Value (KiB)", style="green", justify="right")
            report_table.add_row(
                "ROM Size",
                str(model_report["rom_size"]),
                bytes_to_kib(model_report["rom_size"]),
            )
            report_table.add_row("ROM MACC", str(model_report["rom_n_macc"]), "N/A")
            report_table.add_row(
                "RAM Size",
                str(model_report["ram_size"]),
                bytes_to_kib(model_report["ram_size"]),
            )
            report_table.add_row(
                "RAM IO Size",
                str(sum(model_report["ram_io_size"])),
                bytes_to_kib(sum(model_report["ram_io_size"])),
            )
            report_table.add_row(
                "Model Size",
                str(model_report["model_size"]),
                bytes_to_kib(model_report["model_size"]),
            )
            console.print(report_table)
    if action == "generate":
        args.pop("full_report")
        generate(**args)


def _check_and_download_executable():
    """
    Checks for the stedgeai executable and downloads it if it doesn't exist
    """
    p = inspect.currentframe().f_code.co_name[::-1]
    if EXE_PATH.exists():
        return
    # Create a directory with cubeAI version under exe directory
    EXE_PATH.parent.mkdir(exist_ok=True, parents=True)
    AR_PATH = EXE_PATH.parents[4] / "stedgeai.7z"
    OUT_PATH = EXE_PATH.parents[4]

    with console.status("[green]Preparing stedgeai... Please wait...", spinner="dots"):
        _download(
            f"{REL_URL}/stedgeai.7z",
            str(AR_PATH),
        )
        with py7zr.SevenZipFile(AR_PATH, mode="r", password=p) as z:
            z.extractall(OUT_PATH)

def _download(url, fname):
    """
    Utility function to download a file
    Args:
        url: URL of the file to be downloaded
        fname: Path of the file to be downloaded
    """
    resp = requests.get(url, stream=True)
    with open(fname, "wb") as file:
        for data in resp.iter_content(chunk_size=1024):
            file.write(data)


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

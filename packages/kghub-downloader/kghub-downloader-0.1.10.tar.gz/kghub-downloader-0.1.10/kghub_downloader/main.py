from typing import Optional, List

import typer
from kghub_downloader.download_utils import download_from_yaml

typer_app = typer.Typer()


@typer_app.command()
def main(
         yaml_file: Optional[str] = typer.Argument("download.yaml", help="List of files to download in YAML format"),
         output_dir: Optional[str] = typer.Option("data", help="Path to output directory"),
         ignore_cache: Optional[bool] = typer.Option(False, help="Ignoring already downloaded files and download again"),
         tag: Optional[List[str]] = typer.Option(None, help="Optional list of tags to limit downloading to")
         ):
    download_from_yaml(yaml_file, output_dir, ignore_cache, tag)


if __name__ == "__main__":
    typer_app()

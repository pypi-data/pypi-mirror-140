from collections import defaultdict
import json
from typing import Optional
import typer
import os
import glob
import pathlib

app = typer.Typer()

DEFAULT_EXTENSIONS: dict = {
    "TextFiles": [
        "doc",
        "docx",
        "log",
        "msg",
        "odt",
        "pages",
        "rtf",
        "tex",
        "txt",
        "wpd",
        "wps",
        "gdoc",
    ],
    "DataFiles": [
        "csv",
        "dat",
        "ged",
        "key",
        "keychain",
        "pps",
        "ppt",
        "pptx",
        "sdf",
        "tar",
        "tax2016",
        "tax2018",
        "vcf",
        "xml",
    ],
    "AudioFiles": ["aif", "iff", "m3u", "m4a", "mid", "mp3", "mpa", "wav", "wma"],
    "VideoFiles": [
        "3g2",
        "3gp",
        "asf",
        "avi",
        "flv",
        "m4v",
        "mov",
        "mp4",
        "mpg",
        "rm",
        "srt",
        "swf",
        "vob",
        "wmv",
        "mkv",
    ],
    "3DVideoFiles": ["3dm", "3ds", "max", "obj"],
    "RasterImageFiles": [
        "bmp",
        "dds",
        "gif",
        "jpg",
        "jpeg",
        "png",
        "psd",
        "pspimage",
        "tga",
        "thm",
        "tif",
        "tiff",
        "yuv",
    ],
    "VectorImageFiles": ["ai", "eps", "ps", "svg"],
    "PageLayoutFiles": ["indd", "pct", "pdf"],
    "SpreadsheetFiles": ["xlr", "xls", "xlsx"],
    "DatabaseFiles": ["accdb", "db", "dbf", "mdb", "pdb", "sql"],
    "ExecutableFiles": [
        "apk",
        "app",
        "bat",
        "cgi",
        "com",
        "exe",
        "gadget",
        "jar",
        "wsf",
    ],
    "GameFiles": ["dem", "gam", "nes", "rom", "sav"],
    "CADFiles": ["dwg", "dxf"],
    "GISFiles": ["gpx", "kml", "kmz"],
    "WebFiles": [
        "asp",
        "aspx",
        "cer",
        "cfm",
        "csr",
        "css",
        "html",
        "html",
        "js",
        "jsp",
        "jsx",
        "php",
        "rss",
        "xhtml",
    ],
    "PluginFiles": ["crx", "plugin"],
    "FontFiles": ["fnt", "fon", "otf", "ttf", "woff"],
    "SystemFiles": [
        "cab",
        "cpl",
        "cur",
        "deskthemepack",
        "dll",
        "dmp",
        "drv",
        "icns",
        "ico",
        "lnk",
        "sys",
    ],
    "SettingsFiles": ["cfg", "ini", "prf"],
    "EncodedFiles": ["hqx", "mim", "uue"],
    "CompressedFiles": [
        "7z",
        "cbr",
        "deb",
        "gz",
        "pkg",
        "rar",
        "rpm",
        "sitx",
        "tar.gz",
        "zip",
        "zipx",
    ],
    "DiskImageFiles": ["bin", "cue", "dmg", "iso", "mdf", "toast", "vcd"],
    "DeveloperFiles": [
        "c",
        "class",
        "cpp",
        "cs",
        "dtd",
        "fla",
        "h",
        "java",
        "lua",
        "m",
        "pl",
        "py",
        "sh",
        "sln",
        "sln",
        "swift",
        "vb",
        "vcxproj",
        "xcodeproj",
    ],
    "BackupFiles": ["bak", "tmp"],
    "MiscFiles": ["crdownload", "ics", "msi", "part", "torrent"],
}


def _make_extension_to_folder_object(config: dict = None) -> dict:
    config_object: dict = config if config else DEFAULT_EXTENSIONS
    data: dict = {}
    for folder, extensions in config_object.items():
        for ext in extensions:
            data[ext.lower()] = folder
    return data


def _create_config_file(contents=DEFAULT_EXTENSIONS) -> None:
    extensions_path: str = f'{os.path.expanduser("~")}/.sorter/extensions.json'
    pathlib.Path(extensions_path).parent.mkdir(parents=True, exist_ok=True)
    with open(f'{os.path.expanduser("~")}/.sorter/extensions.json', "w") as f:
        f.write(json.dumps(contents, indent=4))


def _read_config_file() -> dict:
    extensions_path: str = f'{os.path.expanduser("~")}/.sorter/extensions.json'
    if not os.path.exists(extensions_path):
        _create_config_file()
    extensions: dict = {}
    with open(extensions_path, "r") as f:
        extensions = json.load(f)
    return extensions


def get_all_folders_in_path(path: str) -> str:
    folder_names: list = [
        folder_name
        for folder_name in glob.glob(f"{path}/*")
        if os.path.isdir(folder_name)
    ]
    return folder_names


def get_all_files_in_path(path: str) -> str:
    file_names: list = [
        file_name for file_name in glob.glob(f"{path}/*") if os.path.isfile(file_name)
    ]
    return file_names


def get_or_create_dir(dir_name: str) -> str:
    if os.path.exists(dir):
        return dir_name
    os.mkdir(dir_name)
    return dir_name


def get_file_extension(file_name: str) -> Optional[str]:
    if os.path.isfile(file_name):
        return ".".join(pathlib.Path(file_name).suffixes).lower()


def _move_file(filepath: str, new_filepath: str) -> Optional[pathlib.Path]:
    try:
        the_file: pathlib.Path = pathlib.Path(filepath)
        pathlib.Path(new_filepath).parent.mkdir(parents=True, exist_ok=True)
        moved_file: pathlib.Path = the_file.rename(new_filepath)
        return moved_file
    except Exception as e:
        typer.echo(e)
        pass


class FileSorter:
    sorted_files: dict = {}
    extensions: dict = DEFAULT_EXTENSIONS
    _extensions_to_folders: Optional[dict] = None

    def __init__(self) -> None:
        self.extensions: dict = _read_config_file()

    def _reload_extensions(self) -> None:
        self.extensions: dict = _read_config_file()
        self._extensions_to_folders = None

    def _save_extensions(self) -> None:
        data = defaultdict(list)
        for ext, folder in self.extensions_to_folders().items():
            data[folder].append(ext)
        _create_config_file(data)
        self._reload_extensions()

    def save_extensions(self) -> None:
        self._save_extensions()

    def _add_extension(
        self, extension: str, folder_name: str, replace: bool = True
    ) -> bool:
        if self.extensions_to_folders().get(extension):
            if replace:
                self.extensions_to_folders()[extension] = folder_name
                return True
        else:
            self.extensions_to_folders()[extension] = folder_name
            return True

    def _remove_extension(self, extension: str) -> bool:
        try:
            del self.extensions_to_folders()[extension]
            return True
        except Exception as e:
            return False

    def remove_extensions(self, extensions: list) -> bool:
        removed = False
        for extension in extensions:
            removed = self._remove_extension(extension)
        if removed:
            self.save_extensions()
        return removed

    def add_extensions(self, extensions: list, folder_name: str) -> bool:
        added = False
        for extension in extensions:
            added = self._add_extension(extension, folder_name)
        if added:
            self.save_extensions()
        return added

    def extensions_to_folders(self) -> dict:
        if self._extensions_to_folders is None:
            self._extensions_to_folders = _make_extension_to_folder_object(
                self.extensions
            )
        return self._extensions_to_folders

    def _sort_files_in_path(self, path: str) -> dict:
        sorted_files: dict = {}
        extensions = self.extensions_to_folders()
        for p in get_all_files_in_path(path):
            the_file: pathlib.Path = pathlib.Path(p)
            parent_folder: pathlib.Path = the_file.parent
            grouped_folder = extensions.get(get_file_extension(p))
            if grouped_folder:
                new_file_path: str = str(
                    pathlib.Path(f"{parent_folder}/{grouped_folder}/{the_file.name}")
                )
                sorted_files[p] = new_file_path
        return sorted_files

    def _sort(self, path: str, levels: int = 0) -> dict:
        sorted_files: dict = {}
        if os.path.exists(path) and os.path.isdir(path):
            sorted_files.update(self._sort_files_in_path(path))
            # Base case so we stop going thorugh folders at some point
            if levels != 0:
                next_level: int = levels - 1
                for folder_path in get_all_folders_in_path(path):
                    sorted_files.update(self._sort(folder_path, next_level))
        else:
            typer.echo(f"The path '{path}' cannot be found or was not a directory.")
        return sorted_files

    def prepare_files_for_sort(
        self, path: str, levels: int = 0, replace: bool = False
    ) -> dict:
        sorted_files: dict = self._sort(path=path, levels=levels)
        typer.echo(f"Found {len(sorted_files.keys())} files")
        if replace:
            self.sorted_files = sorted_files
        else:
            self.sorted_files.update(sorted_files)
        return sorted_files

    def move_prepared_files(self, dry_run: bool = False) -> None:
        count: int = len(self.sorted_files.keys())
        if dry_run:
            typer.echo("DRY RUN\n" * 3)
        typer.echo(f"Sorting {count} file(s)")
        stars: str = len(f"Sorting {count} file(s)") * "*"
        typer.echo(stars)
        for index, file_data in enumerate(self.sorted_files.items(), start=1):
            typer.echo("*")
            typer.echo(f"* Sorting file {index}/{count}")
            filepath, new_filepath = file_data
            new_file = (
                new_filepath
                if dry_run
                else _move_file(filepath, new_filepath).resolve()
            )
            typer.echo("*")
            if new_file:
                typer.echo(f"* {'Would have m' if dry_run else 'M'}oved to: {new_file}")
            else:
                typer.echo(f"* Failed to move file")
            typer.echo("*")
            typer.echo(stars)


@app.command(
    help="Prints out an alphabetical list of extensions and the folders they will be sorted into."
)
def list_extensions():
    sorter: FileSorter = FileSorter()
    extensions = sorter.extensions_to_folders()
    for key in sorted(extensions.keys()):
        typer.echo(f"{key}: {extensions[key]}")


@app.command(help="Adds the given extensions to the given folder")
def remove_extensions(
    ext: str = typer.Option(
        default=None, prompt="Enter a list of extensions separated by commas"
    )
):
    extensions = [extension.strip(" .").lower() for extension in ext.split(",")]
    sorter: FileSorter = FileSorter()
    if sorter.remove_extensions(extensions):
        typer.echo("Removed extensions")


@app.command(help="Link extensions to a folder for when sorting occurs.")
def add_extensions(
    folder: str = typer.Option(
        default=None,
        prompt="Enter a folder name for the extensions to be grouped into.",
        help="A folder name that extensions will be grouped in.",
    ),
    ext: str = typer.Option(
        default=None,
        prompt="Enter a list of extensions separated by commas",
        help="A comma separated list of extensions. Extensions will be stripped of whitespace and periods, and forced to lowercase",
    ),
):
    extensions = [extension.strip(" .").lower() for extension in ext.split(",")]
    sorter: FileSorter = FileSorter()
    if sorter.add_extensions(extensions, folder):
        typer.echo("Added extensions")


@app.command(
    help="Sorts the files of a folder, or the current working directory if none is given."
)
def sort(
    path: str = typer.Option(
        default=os.getcwd(), help="A path to a directory on your computer to sort"
    ),
    levels: int = typer.Option(
        default=0,
        help="-1 to sort all folders and their children, 0 to sort no folders, anything greater than 0 to sort that many children",
    ),
    dry_run: bool = typer.Option(
        default=False,
        help="Include this to do a dry-run of the file(s) that would be sorted",
    ),
):
    sorter: FileSorter = FileSorter()
    if "~" in path:
        path = os.path.expanduser(path)
    sorter.prepare_files_for_sort(path, levels=levels)
    sorter.move_prepared_files(dry_run=dry_run)


"""
TODO:
 - Support the default config/extensions object
 - Pull in folder names for extensions from the config files
 - Refactor into a class?
"""

if __name__ == "__main__":
    app()

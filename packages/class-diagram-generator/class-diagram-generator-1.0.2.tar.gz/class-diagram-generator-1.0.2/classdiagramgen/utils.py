from os.path import join, relpath, isfile, isdir
from os import walk
from fnmatch import fnmatch
from typing import Iterable, Optional
from PIL import Image

from .class_diagram import render_diagrams, merge_same_diagrams
from .csharp_analyser import extract_diagrams

def is_file_included(filename: str, included: list[str], excluded: list[str]) -> bool:
    lower_filename = filename.lower()
    if not any(fnmatch(lower_filename, pattern) for pattern in included):
        return False

    if any(fnmatch(lower_filename, pattern) for pattern in excluded):
        return False

    return True

def list_files(folder_path: str, included: list[str], excluded: list[str]) -> Iterable[str]:
    for (root, _, files) in walk(folder_path, topdown=True):
        for name in files:
            full_path = join(root, name)
            if is_file_included(relpath(full_path, folder_path), included, excluded):
                yield full_path

def render_from_paths(*paths: str, font_file: str, font_size: int) -> Optional[Image.Image]:
    included_files = ["*.cs"]
    excluded_files = ["*.designer.cs", "**/obj/**", "**/bin/**", "**/properties/**"]
    diagrams = []

    for path in paths:
        if isfile(path):
            if is_file_included(path, included_files, excluded_files):
                for diagram in extract_diagrams(path):
                    diagrams.append(diagram)
        elif isdir(path):
            for filename in list_files(path, included_files, excluded_files):
                print(filename)
                for diagram in extract_diagrams(filename):
                    diagrams.append(diagram)


    merge_same_diagrams(diagrams)

    if len(diagrams) > 0:
        return render_diagrams(diagrams, font_file, font_size)
    else:
        return None

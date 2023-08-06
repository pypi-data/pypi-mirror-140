"""
Adobe DNG SDK Conversion Process
================================

Defines various objects implementing raw conversion based on *Adobe DNG SDK*
and *dcraw*:

-   :func:`colour_hdri.convert_raw_files_to_dng_files`
-   :func:`colour_hdri.convert_dng_files_to_intermediate_files`
-   :func:`colour_hdri.read_dng_files_exif_tags`
"""

from __future__ import annotations

import logging
import numpy as np
import os
import platform
import re
import shlex
import subprocess  # nosec

from colour.hints import (
    Callable,
    Boolean,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)
from colour.utilities import CaseInsensitiveMapping, warning
from colour.utilities.documentation import (
    DocstringText,
    is_documentation_building,
)

from colour_hdri.utilities import (
    EXIFTag,
    parse_exif_array,
    parse_exif_number,
    parse_exif_string,
    path_exists,
    read_exif_tags,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2015 Colour Developers"
__license__ = "New BSD License - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "RAW_CONVERTER",
    "RAW_CONVERSION_ARGUMENTS",
    "RAW_D_CONVERSION_ARGUMENTS",
    "DNG_CONVERTER",
    "DNG_CONVERSION_ARGUMENTS",
    "DNG_EXIF_TAGS_BINDING",
    "convert_raw_files_to_dng_files",
    "convert_dng_files_to_intermediate_files",
    "read_dng_files_exif_tags",
]

_IS_MACOS_PLATFORM: Boolean = platform.system() == "Darwin"
"""Whether the current platform is *macOS*."""

_IS_WINDOWS_PLATFORM: Boolean = platform.system() in ("Windows", "Microsoft")
"""Whether the current platform is *Windows*."""

RAW_CONVERTER: str = "dcraw"
if is_documentation_building():  # pragma: no cover
    RAW_CONVERTER = DocstringText(RAW_CONVERTER)
    RAW_CONVERTER.__doc__ = """
Command line raw conversion application, usually Dave Coffin's *dcraw*.
"""

RAW_CONVERSION_ARGUMENTS: str = '-t 0 -D -W -4 -T "{0}"'
if _IS_WINDOWS_PLATFORM:
    RAW_CONVERSION_ARGUMENTS = RAW_CONVERSION_ARGUMENTS.replace('"', "")
if is_documentation_building():  # pragma: no cover
    RAW_CONVERSION_ARGUMENTS = DocstringText(RAW_CONVERSION_ARGUMENTS)
    RAW_CONVERSION_ARGUMENTS.__doc__ = """
Arguments for the command line raw conversion application for non
demosaiced linear *tiff* file format output.
"""

RAW_D_CONVERSION_ARGUMENTS: str = '-t 0 -H 1 -r 1 1 1 1 -4 -q 3 -o 0 -T "{0}"'
if _IS_WINDOWS_PLATFORM:
    RAW_D_CONVERSION_ARGUMENTS = RAW_D_CONVERSION_ARGUMENTS.replace('"', "")
if is_documentation_building():  # pragma: no cover
    RAW_D_CONVERSION_ARGUMENTS = DocstringText(RAW_D_CONVERSION_ARGUMENTS)
    RAW_D_CONVERSION_ARGUMENTS.__doc__ = """
Arguments for the command line raw conversion application for demosaiced
linear *tiff* file format output.
"""

if _IS_MACOS_PLATFORM:
    DNG_CONVERTER: Optional[str] = (
        "/Applications/Adobe DNG Converter.app/Contents/"
        "MacOS/Adobe DNG Converter"
    )
elif _IS_WINDOWS_PLATFORM:
    DNG_CONVERTER: Optional[  # type: ignore[no-redef]
        str
    ] = "Adobe DNG Converter"
else:
    warning('"Adobe DNG Converter" is not available on your platform!')
    DNG_CONVERTER: Optional[str] = None  # type: ignore[no-redef]

if DNG_CONVERTER is not None:
    if is_documentation_building():  # pragma: no cover
        DNG_CONVERTER = DocstringText(DNG_CONVERTER)
        DNG_CONVERTER.__doc__ = """
Command line *DNG* conversion application, usually *Adobe DNG Converter*.
"""

DNG_CONVERSION_ARGUMENTS: str = '-cr7.1 -l -d "{0}" "{1}"'
if _IS_WINDOWS_PLATFORM:
    DNG_CONVERSION_ARGUMENTS = DNG_CONVERSION_ARGUMENTS.replace('"', "")
if is_documentation_building():  # pragma: no cover
    DNG_CONVERSION_ARGUMENTS = DocstringText(DNG_CONVERSION_ARGUMENTS)
    DNG_CONVERSION_ARGUMENTS.__doc__ = """
Arguments for the command line *dng* conversion application.
"""

DNG_EXIF_TAGS_BINDING: CaseInsensitiveMapping = CaseInsensitiveMapping(
    {
        "EXIF": CaseInsensitiveMapping(
            {
                "Make": (parse_exif_string, None),
                "Camera Model Name": (parse_exif_string, None),
                "Camera Serial Number": (parse_exif_string, None),
                "Lens Model": (parse_exif_string, None),
                "DNG Lens Info": (parse_exif_string, None),
                "Focal Length": (parse_exif_number, None),
                "Exposure Time": (parse_exif_number, None),
                "F Number": (parse_exif_number, None),
                "ISO": (parse_exif_number, None),
                "CFA Pattern 2": (
                    lambda x: parse_exif_array(x, np.int_),
                    None,
                ),
                "CFA Plane Color": (
                    lambda x: parse_exif_array(x, np.int_),
                    None,
                ),
                "Black Level Repeat Dim": (
                    lambda x: parse_exif_array(x, np.int_),
                    None,
                ),
                "Black Level": (lambda x: parse_exif_array(x, np.int_), None),
                "White Level": (lambda x: parse_exif_array(x, np.int_), None),
                "Samples Per Pixel": (
                    lambda x: parse_exif_number(x, np.int_),
                    None,
                ),
                "Active Area": (lambda x: parse_exif_array(x, np.int_), None),
                "Orientation": (lambda x: parse_exif_number(x, np.int_), None),
                "Camera Calibration Sig": (parse_exif_string, None),
                "Profile Calibration Sig": (parse_exif_string, None),
                "Calibration Illuminant 1": (
                    lambda x: parse_exif_number(x, np.int_),
                    17,
                ),
                "Calibration Illuminant 2": (
                    lambda x: parse_exif_number(x, np.int_),
                    21,
                ),
                "Color Matrix 1": (
                    lambda x: parse_exif_array(x, np.float_, (3, 3)),
                    "1 0 0 0 1 0 0 0 1",
                ),
                "Color Matrix 2": (
                    lambda x: parse_exif_array(x, np.float_, (3, 3)),
                    "1 0 0 0 1 0 0 0 1",
                ),
                "Camera Calibration 1": (
                    lambda x: parse_exif_array(x, np.float_, (3, 3)),
                    "1 0 0 0 1 0 0 0 1",
                ),
                "Camera Calibration 2": (
                    lambda x: parse_exif_array(x, np.float_, (3, 3)),
                    "1 0 0 0 1 0 0 0 1",
                ),
                "Analog Balance": (
                    lambda x: parse_exif_array(x, np.float_),
                    "1 1 1",
                ),
                "Reduction Matrix 1": (
                    lambda x: parse_exif_array(x, np.float_, (3, 3)),
                    "1 0 0 0 1 0 0 0 1",
                ),
                "Reduction Matrix 2": (
                    lambda x: parse_exif_array(x, np.float_, (3, 3)),
                    "1 0 0 0 1 0 0 0 1",
                ),
                "Forward Matrix 1": (
                    lambda x: parse_exif_array(x, np.float_, (3, 3)),
                    "1 0 0 0 1 0 0 0 1",
                ),
                "Forward Matrix 2": (
                    lambda x: parse_exif_array(x, np.float_, (3, 3)),
                    "1 0 0 0 1 0 0 0 1",
                ),
                "As Shot Neutral": (
                    lambda x: parse_exif_array(x, np.float_),
                    "1 1 1",
                ),
                "Baseline Exposure": (
                    lambda x: parse_exif_number(x, np.float_),
                    None,
                ),
                "Baseline Noise": (
                    lambda x: parse_exif_number(x, np.float_),
                    None,
                ),
            }
        )
    }
)
DNG_EXIF_TAGS_BINDING.__doc__ = """
Exif tags binding for a *dng* file.
"""


def convert_raw_files_to_dng_files(
    raw_files: Sequence[str], output_directory: str
) -> List[str]:
    """
    Convert given raw files to *dng* files using given output directory.

    Parameters
    ----------
    raw_files
        Raw files to convert to *dng* files.
    output_directory
        Output directory.

    Returns
    -------
    :class:`list`
        *dng* files.

    Raises
    ------
    RuntimeError
        If the *Adobe DNG Converter* is not available.
    """

    if DNG_CONVERTER is not None:
        dng_files = []
        for raw_file in raw_files:
            raw_file_extension = os.path.splitext(raw_file)[1]
            dng_file = os.path.join(
                output_directory,
                os.path.basename(
                    re.sub(f"{raw_file_extension}$", ".dng", raw_file)
                ),
            )

            if path_exists(dng_file):
                os.remove(dng_file)

            logging.info(f'Converting "{raw_file}" file to "{dng_file}" file.')

            command = [DNG_CONVERTER] + shlex.split(
                DNG_CONVERSION_ARGUMENTS.format(output_directory, raw_file),
                posix=not _IS_WINDOWS_PLATFORM,
            )

            subprocess.call(command, shell=_IS_WINDOWS_PLATFORM)  # nosec

            dng_files.append(dng_file)

        return dng_files
    else:
        raise RuntimeError('The "Adobe DNG Converter" is not available!')


def convert_dng_files_to_intermediate_files(
    dng_files: Sequence[str],
    output_directory: str,
    demosaicing: Boolean = False,
) -> List[str]:
    """
    Convert given *dng* files to intermediate *tiff* files using given output
    directory.

    Parameters
    ----------
    dng_files
        *dng* files to convert to intermediate *tiff* files.
    output_directory
        Output directory.
    demosaicing
        Perform demosaicing on conversion.

    Returns
    -------
    :class:`list`
        Intermediate *tiff* files.
    """

    intermediate_files = []
    for dng_file in dng_files:
        intermediate_file = re.sub("\\.dng$", ".tiff", dng_file)

        if path_exists(intermediate_file):
            os.remove(intermediate_file)

        logging.info(
            f'Converting "{dng_file}" file to "{intermediate_file}" file.'
        )

        raw_conversion_arguments = (
            RAW_D_CONVERSION_ARGUMENTS
            if demosaicing
            else RAW_CONVERSION_ARGUMENTS
        )
        command = [RAW_CONVERTER] + shlex.split(
            raw_conversion_arguments.format(dng_file),
            posix=not _IS_WINDOWS_PLATFORM,
        )

        subprocess.call(command, shell=_IS_WINDOWS_PLATFORM)  # nosec

        tiff_file = os.path.join(
            output_directory, os.path.basename(intermediate_file)
        )
        if tiff_file != intermediate_file:
            if path_exists(tiff_file):
                os.remove(tiff_file)

            os.rename(intermediate_file, tiff_file)

        intermediate_files.append(tiff_file)

    return intermediate_files


def read_dng_files_exif_tags(
    dng_files: Sequence[str],
    exif_tags_binding: Mapping[
        str, Mapping[str, Tuple[Callable, Optional[str]]]
    ] = DNG_EXIF_TAGS_BINDING,
) -> List[CaseInsensitiveMapping]:
    """
    Read given *dng* files exif tags using given binding.

    Parameters
    ----------
    dng_files
        *dng* files to read the exif tags from.
    exif_tags_binding
        Exif tags binding.

    Returns
    -------
    :class:`list`
        *dng* files exif tags.
    """

    dng_files_exif_tags = []
    for dng_file in dng_files:
        exif_tags = read_exif_tags(dng_file)
        binding = CaseInsensitiveMapping()
        for group, tags in exif_tags_binding.items():
            binding[group] = CaseInsensitiveMapping()
            for tag, (parser, default) in tags.items():
                exif_tag = exif_tags[group].get(tag)
                if exif_tag is None:
                    binding[group][tag] = (
                        default
                        if default is None
                        else parser(EXIFTag(value=default))
                    )
                else:
                    binding[group][tag] = parser(exif_tag[0])

        dng_files_exif_tags.append(binding)

    return dng_files_exif_tags

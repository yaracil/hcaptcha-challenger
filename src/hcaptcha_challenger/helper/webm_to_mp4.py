"""
WebM to MP4 conversion tool

This script can convert .webm video files to .mp4 format.
Supports single file conversion or batch conversion of all .webm files in the entire directory.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, List

from loguru import logger

INVALID_PATH_CHARS = set("|;&$`")


def _validate_path(path: str, expected_suffix: Optional[str] = None) -> Path:
    """Validate a filesystem path and optionally enforce its suffix.

    Args:
        path: Path supplied by the user.
        expected_suffix: Require the path to end with this suffix when provided.

    Returns:
        Path: Resolved ``Path`` object.

    Raises:
        ValueError: If the path contains disallowed characters or does not match the
            expected suffix.
    """

    if any(c in path for c in INVALID_PATH_CHARS):
        raise ValueError(f"Unsafe path: {path}")

    p = Path(path).expanduser().resolve()
    if expected_suffix and p.suffix.lower() != expected_suffix:
        raise ValueError(f"Invalid suffix for {p}: expected {expected_suffix}")
    return p


def convert_webm_to_mp4(input_file: str, output_file: Optional[str] = None) -> bool:
    """Convert a single WebM file to MP4 format with basic path validation."""

    try:
        input_path = _validate_path(input_file, ".webm")
        output_path = (
            _validate_path(output_file, ".mp4") if output_file else input_path.with_suffix(".mp4")
        )
    except ValueError as exc:
        logger.error(str(exc))
        return False

    if not input_path.exists():
        logger.error(f"Input file does not exist: {input_path}")
        return False

    try:
        import ffmpeg

        logger.info(f"Converting: {input_path} -> {output_path}")

        (
            ffmpeg.input(str(input_path))
            .output(
                str(output_path),
                vcodec="libx264",
                acodec="aac",
                audio_bitrate="192k",
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )

        logger.success(f"Conversion successfully: {output_path}")
        return True

    except ffmpeg.Error as e:  # type: ignore[name-defined]
        logger.error(
            f"Conversion failed: {e.stderr.decode('utf-8') if getattr(e, 'stderr', None) else e}"
        )
        return False
    except Exception as e:  # pragma: no cover - unexpected errors
        logger.exception(f"An error occurred during the conversion process: {e}")
        return False


def batch_convert(input_dir: str, output_dir: Optional[str] = None) -> None:
    """Batch convert all WebM files in the directory."""

    try:
        input_dir_path = _validate_path(input_dir)
        output_dir_path = _validate_path(output_dir) if output_dir else None
    except ValueError as exc:
        logger.error(str(exc))
        return

    if not input_dir_path.is_dir():
        logger.error(f"The input directory does not exist: {input_dir_path}")
        return

    if output_dir_path and not output_dir_path.exists():
        output_dir_path.mkdir(parents=True)
        logger.info(f"Create output directory: {output_dir_path}")

    # Get all .webm files
    webm_files = list(input_dir_path.glob("**/*.webm"))

    if not webm_files:
        logger.warning(f"No .webm file was found in {input_dir}")
        return

    logger.info(f"Found {len(webm_files)} .webm files")

    success_count = 0
    for webm_file in webm_files:
        if output_dir_path:
            # Calculate relative paths and maintain directory structure
            rel_path = webm_file.relative_to(input_dir_path)
            output_file = output_dir_path / rel_path.with_suffix('.mp4')

            # Make sure the output directory exists
            os.makedirs(output_file.parent, exist_ok=True)

            if convert_webm_to_mp4(str(webm_file), str(output_file)):
                success_count += 1
        else:
            if convert_webm_to_mp4(str(webm_file)):
                success_count += 1

    logger.info(
        f"Conversion completed: {success_count}/{len(webm_files)} files were successfully converted"
    )


def check_ffmpeg() -> bool:
    """Check if the system is installed ffmpeg"""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False


def invoke(
    input_path: str, output_path: Optional[str] = None, is_directory: bool = False
) -> List[dict]:
    """
    Call the conversion function programmatically

        Args:
            input_path: The input WebM file path or the directory path containing the WebM file
            output_path: The output MP4 file path or directory, automatically generated if not specified
            is_directory: Whether to batch process the directory

        Returns:
            List[dict]: A list of conversion results, each dictionary contains input file, output file, and conversion status
    """
    # Check if ffmpeg is installed
    if not check_ffmpeg():
        raise RuntimeError("ffmpeg not found. Please install ffmpeg before running this function.")

    results = []

    if is_directory:
        input_dir = _validate_path(input_path)
        output_dir = _validate_path(output_path) if output_path else None

        if not input_dir.is_dir():
            raise ValueError(f"Input directory does not exist: {input_dir}")

        if output_dir and not output_dir.exists():
            output_dir.mkdir(parents=True)

        webm_files = list(input_dir.glob("**/*.webm"))

        for webm_file in webm_files:
            if output_dir:
                rel_path = webm_file.relative_to(input_dir)
                output_file = output_dir / rel_path.with_suffix('.mp4')
                output_file.parent.mkdir(parents=True, exist_ok=True)
                success = convert_webm_to_mp4(str(webm_file), str(output_file))
            else:
                output_file = webm_file.with_suffix('.mp4')
                success = convert_webm_to_mp4(str(webm_file))

            results.append(
                {"input_file": str(webm_file), "output_file": str(output_file), "success": success}
            )
    else:
        input_file = _validate_path(input_path, ".webm")
        output_file = _validate_path(output_path, ".mp4") if output_path else None

        if not input_file.exists():
            raise ValueError(f"Input file does not exist: {input_file}")

        success = convert_webm_to_mp4(str(input_file), str(output_file) if output_file else None)

        if not output_file:
            output_file = input_file.with_suffix('.mp4')

        results.append(
            {"input_file": str(input_file), "output_file": str(output_file), "success": success}
        )

    return results

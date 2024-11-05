"""Program that copies and sorts files by their extension"""

import logging
import asyncio
import argparse
from collections import defaultdict
from aiopath import AsyncPath  # Ensure AsyncPath is used correctly
import aioshutil


def parse_arguments():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source_folder", type=str, help="Source folder path", required=True
    )
    parser.add_argument(
        "--output_folder", type=str, help="Output folder path", required=True
    )
    return parser.parse_args()


async def read_folder(source_folder, files):
    """Function checks if the path is a file or a folder"""
    try:
        async for path in source_folder.iterdir():
            if await path.is_file():
                files[path.suffix].append(path)
            elif await path.is_dir():
                await read_folder(path, files)
    except Exception as e:
        logging.error(f"Error reading folder {source_folder}: {e}")


async def copy_file(file, output_folder):
    """Function copies the file to the output folder"""
    try:
        await aioshutil.copy(file, output_folder / file.name)
    except Exception as e:
        logging.error(f"Error copying file {file} to {output_folder}: {e}")


async def main():
    """Main function that sorts the files"""
    args = parse_arguments()
    source_folder = AsyncPath(args.source_folder)
    output_folder = AsyncPath(args.output_folder)
    files = defaultdict(list)

    await read_folder(source_folder, files)

    tasks = []
    for ext, ext_files in files.items():
        ext_folder = output_folder / ext
        await ext_folder.mkdir(parents=True, exist_ok=True)
        tasks.extend([copy_file(file, ext_folder) for file in ext_files])

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    asyncio.run(main())

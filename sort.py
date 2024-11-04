import asyncio
import argparse
import logging
from collections import defaultdict
import aiopath
import aioshutil
import warnings

logging.basicConfig(level=logging.ERROR)


def ArgumentParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_folder", type=str, help="Source folder path")
    parser.add_argument("--output_folder", type=str, help="Output folder path")
    return parser.parse_args()


async def read_folder(source_folder, files):
    async for path in source_folder.iterdir():
        if await path.is_file():
            files[path.suffix].append(path)
        elif await path.is_dir():
            await read_folder(path, files)


async def copy_file(file, output_folder):
    await aioshutil.copy(file, output_folder / file.name)


async def main():
    args = ArgumentParser()
    source_folder = aiopath.Path(args.source_folder)
    output_folder = aiopath.Path(args.output_folder)
    files = defaultdict(list)
    await read_folder(source_folder, files)
    for ext, files in files.items():
        ext_folder = output_folder / ext
        await ext_folder.mkdir(parents=True, exist_ok=True)
        await asyncio.gather(*[copy_file(file, ext_folder) for file in files])


if __name__ == "__main__":
    asyncio.run(main())
    warnings.filterwarnings("ignore", category=RuntimeWarning)

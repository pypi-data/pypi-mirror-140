import argparse
import os

from bobthebuilder.builder import BobBuilder


def build_cli():
    args = argparse.ArgumentParser(description="Сборщик проектов на defold")
    args.add_argument('-p', choices=['js-web'], dest='platform', help='Build platform.', required=True)
    args.add_argument('-a', choices=['js-web', 'js-web,wasm-web'], dest='arch', help='Build Architecture', required=True)
    args.add_argument('-d', help='Game project directory')
    args.add_argument('-o', help='Compiled artifact directory', dest='out_dir', required=True)
    parsed = args.parse_args()
    project_dir = parsed.d if parsed.d else os.getcwd()
    bob = BobBuilder(project_dir)
    bob.resolve_deps()
    bob.build(parsed.platform, parsed.arch)
    bob.bundle(parsed.out_dir, platform=parsed.platform, arch=parsed.arch, variant='debug')


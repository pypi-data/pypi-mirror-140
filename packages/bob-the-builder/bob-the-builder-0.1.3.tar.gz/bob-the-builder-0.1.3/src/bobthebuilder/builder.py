import subprocess
import logging
import pathlib

class BobBuilder:
    def __init__(self, project_dir: str) -> None:
        abs_path = str(pathlib.Path(project_dir).resolve())
        self.common_args = [
            '--verbose', 
            '--root', abs_path, 
            '--input', abs_path
        ]
        self.exec = ['java', '-jar', 'bob.jar']
        self.project_dir = abs_path
    
    def resolve_deps(self):
        cmd = 'resolve'
        exec_cmd = self.exec + self.common_args + [cmd]
        result = self._exec_cmd(exec_cmd)
            
    def build(self, platform: str, arch: str):
        cmd = 'build'
        args = [
            '--archive',
            '--platform', platform,
            '--architectures', arch,
        ]
        exec_cmd = self.exec + self.common_args + args + [cmd]
        result = self._exec_cmd(exec_cmd)

    def bundle(self, output_dir: str, platform: str, arch: str, variant: str = 'release'):
        out_dir = str(pathlib.Path(output_dir).resolve())
        cmd = 'bundle'
        args = [ 
            '--bundle-output', out_dir,
            '--platform', platform,
            '--architectures', arch,
            '--variant', variant
        ]
        exec_cmd = self.exec + self.common_args + args + [cmd]
        result = self._exec_cmd(exec_cmd)

    def _exec_cmd(self, cmd) -> subprocess.CompletedProcess:
        result = subprocess.run(cmd, check=True)
        return result

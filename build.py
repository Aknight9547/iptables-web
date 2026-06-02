#!/usr/bin/env python3
import os
import sys
import tarfile
import shutil
import argparse
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description='Build iptables-web package')
    parser.add_argument('--version', '-v', help='Specify version number')
    parser.add_argument('--output', '-o', default='dist', help='Output directory')
    parser.add_argument('--include-deps', default=True, action='store_true', help='Include Python dependencies')
    parser.add_argument('--no-deps', dest='include_deps', action='store_false', help='Do not include Python dependencies')
    return parser.parse_args()

def get_version(args):
    if args.version:
        return args.version
    return datetime.now().strftime('%Y%m%d%H%M')

def create_dist_dir(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def copy_source_files(src_dir, dest_dir):
    files_to_copy = [
        'app.py',
        'config.py',
        'requirements.txt',
        'iptables_manager.py',
        'models.py',
        'deploy.sh'
    ]
    
    dirs_to_copy = [
        'routes',
        'templates',
        'static'
    ]
    
    for file in files_to_copy:
        src_path = os.path.join(src_dir, file)
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_dir)
            print(f'Copied: {file}')
    
    for dirname in dirs_to_copy:
        src_path = os.path.join(src_dir, dirname)
        dest_path = os.path.join(dest_dir, dirname)
        if os.path.exists(src_path):
            shutil.copytree(src_path, dest_path)
            print(f'Copied: {dirname}/')

def download_dependencies(dest_dir):
    deps_dir = os.path.join(dest_dir, 'deps')
    os.makedirs(deps_dir, exist_ok=True)
    
    print('Downloading Python dependencies...')
    os.system(f'pip download -r requirements.txt -d {deps_dir}')
    print('Dependencies downloaded.')

def create_version_file(dest_dir, version):
    with open(os.path.join(dest_dir, 'VERSION'), 'w') as f:
        f.write(version)

def create_tarball(source_dir, output_dir, version):
    tarball_name = f'iptables-web-{version}.tar.gz'
    tarball_path = os.path.join(output_dir, tarball_name)
    
    with tarfile.open(tarball_path, 'w:gz') as tar:
        tar.add(source_dir, arcname=f'iptables-web-{version}')
    
    print(f'Created tarball: {tarball_path}')
    return tarball_path

def main():
    args = parse_args()
    version = get_version(args)
    output_dir = create_dist_dir(args.output)
    
    temp_dir = os.path.join(output_dir, f'iptables-web-{version}')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    copy_source_files('.', temp_dir)
    
    if args.include_deps:
        download_dependencies(temp_dir)
    
    create_version_file(temp_dir, version)
    
    create_tarball(temp_dir, output_dir, version)
    
    shutil.rmtree(temp_dir)
    
    print(f'\nBuild completed successfully!')
    print(f'Package: {output_dir}/iptables-web-{version}.tar.gz')

if __name__ == '__main__':
    main()
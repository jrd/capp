#!/usr/bin/env python3
from argparse import ArgumentParser
from contextlib import contextmanager
from functools import partial
from hashlib import sha256
from io import StringIO
from json import load
from os import (
    chdir,
    remove,
)
from pathlib import Path
from re import match
from shutil import rmtree
from subprocess import run
from tarfile import is_tarfile
from tarfile import open as taropen
from tempfile import (
    mkdtemp,
    mkstemp,
)

try:
    from yaml import full_load
except ImportError:
    from sys import (
        exit,
        stderr,
    )
    print("PyYAML/python-yaml should be installed", file=stderr)
    exit(1)


def verify_checksum(dca_path):
    CHUNK_SIZE = 1024 * 1024  # 1 MB
    with open(dca_path.with_suffix(dca_path.suffix + '.sha256'), 'r') as f:
        csum = f.read().strip().split(' ')[0]
    h = sha256()
    with open(dca_path, 'rb') as f:
        for chunk in iter(partial(f.read, CHUNK_SIZE), b''):
            h.update(chunk)
    computed_csum = h.hexdigest()
    if csum != computed_csum:
        raise ValueError('Checksum mismatch')


@contextmanager
def temp_dir():
    tmp_dir = Path(mkdtemp())
    try:
        yield tmp_dir
    finally:
        rmtree(tmp_dir)


@contextmanager
def extract_archive(dca_path):
    with temp_dir() as tmp_dir:
        if not is_tarfile(dca_path):
            raise ValueError(f"{dca_path} is not a valid TAR archive")
        with taropen(dca_path, 'r:gz') as tar:
            if any([
                not (m.isdir() or m.isfile())
                or m.name.startswith('/')
                or '..' in m.name
                for m in tar.getmembers()
            ]):
                raise ValueError(f"{dca_path} is not a safe TAR archive")
            tar.extractall(path=tmp_dir)
        yield tmp_dir


def verify_files_presence(tmp_dir):
    context_found = False
    images_found = False
    metadata_found = False
    for m in tmp_dir.iterdir():
        if m.is_dir() and m.name == 'context':
            context_found = True
        elif m.is_dir() and m.name == 'images':
            images_found = True
        elif m.is_file() and m.name == 'metadata':
            metadata_found = True
    if not context_found:
        raise ValueError("context directory not found in DCA")
    if not images_found:
        raise ValueError("images directory not found in DCA")
    if not metadata_found:
        raise ValueError("metadata file not found in DCA")
    if not (tmp_dir / 'context' / 'docker-compose.yml').is_file():
        raise ValueError("context/docker-compose.yml file not found in DCA")


def verify_compose(version, compose):
    code = run(['docker-compose', '-f', str(compose), 'config', '-q'], capture_output=True).returncode
    if code != 0:
        raise ValueError(f'{compose} is incorrect')
    svc_names = []
    with open(compose) as f:
        dc = full_load(f)
    dc_version = float(dc.get('version', '3'))
    if not 2.2 <= dc_version < 3:
        raise ValueError("docker compose version should be in [2.2; 3[ range")
    for svc_name, svc_def in dc.get('services', {}).items():
        svc_names.append(svc_name)
        if version > 1:
            verify_compose_service(svc_name, svc_def)
    if version > 1:
        for vol_name, vol_def in dc.get('volumes', {}).items():
            verify_compose_volume(vol_name, vol_def)
        for net_name, net_def in dc.get('networks', {}).items():
            verify_compose_network(net_name, net_def)
        for res_name, res_def in dc.get('x-resources', {}).items():
            verify_resources(res_name, res_def)
    return svc_names


def verify_compose_service(name, definition):
    for key in definition.keys():
        if key not in (
            'build',
            'cap_drop',
            'command',
            'depends_on',
            'entrypoint',
            'env_file',
            'environment',
            'expose',
            'extends',
            'extra_hosts',
            'group_add',
            'healthcheck',
            'image',
            'init',
            'labels',
            'networks',
            'pid',
            'scale',
            'stop_grace_period',
            'stop_signal',
            'sysctls',
            'tmpfs',
            'ulimits',
            'volumes',
            'volumes_from',
            'restart',
            'shm_size',
            'tty',
            'user',
            'working_dir',
        ):
            raise ValueError(f"key {key}, defined for {name} is not allowed in services section")
        if key == 'build':
            build_def = definition[key]
            if isinstance(build_def, dict):
                for subkey in build_def.keys():
                    if subkey not in (
                        'context',
                        'dockerfile',
                        'args',
                        'cache_from',
                        'extra_hosts',
                        'labels',
                        'shm_size',
                        'target',
                    ):
                        raise ValueError(f"key {subkey}, defined for {name}.{key} is not allowed in services section")
        elif key == 'extends':
            for subkey in definition[key].keys():
                if subkey not in (
                    'file',
                    'service',
                ):
                    raise ValueError(f"key {subkey}, defined for {name}.{key} is not allowed in services section")
        elif key == 'healthcheck':
            for subkey in definition[key].keys():
                if subkey not in (
                    'test',
                    'interval',
                    'timeout',
                    'retries',
                    'start_period',
                    'disable',
                ):
                    raise ValueError(f"key {subkey}, defined for {name}.{key} is not allowed in services section")
        elif key == 'pid':
            if definition[key] == 'host':
                raise ValueError(f"key {key}, defined for {name} is not allowed to take the 'host' value in services section")
        elif key == 'volumes':
            volumes = definition[key]
            for volume in volumes:
                if isinstance(volume, str):
                    if ':' in volume and not match(r'[a-zA-Z]', volume) and not volume.startswith('./'):
                        raise ValueError(f"The volume {volume}, defined for {name} is not allowed to have a non local source path or non-named volume in services section")
                else:
                    vol_src = volume.get('source', '')
                    if vol_src and not match(r'[a-zA-Z]', vol_src) and not vol_src.startswith('./'):
                        raise ValueError(f"The volume {volume}, defined for {name} is not allowed to have a non local source path or non-named volume in services section")


def verify_compose_volume(name, definition):
    for key in (definition or {}).keys():
        if key not in ('external', 'labels', 'name'):
            raise ValueError(f"key {key}, defined for {name} is not allowed in volumes section")


def verify_compose_network(name, definition):
    for key in (definition or {}).keys():
        if key not in ('external', 'internal', 'labels', 'name'):
            raise ValueError(f"key {key}, defined for {name} is not allowed in networks section")


def verify_resources(name, definition):
    for key in (definition or {}).keys():
        if key not in ('memory', 'memory_avg', 'cpu'):
            raise ValueError(f"key {key}, defined for {name} is not allowed in x-resources section")
        elif key == 'cpu':
            if definition[key] < 1 or definition[key] > 16:
                raise ValueError(f"key {key}, defined for {name} should have a value between [1; 16], in x-resources section")
        else:
            if not any((
                definition[key].endswith('B'),
                definition[key].endswith('K'),
                definition[key].endswith('M'),
                definition[key].endswith('G'),
            )):
                raise ValueError(f"key {key}, defined for {name} should have a unit value of B, K, M or G, in x-resources section")
            value = definition[key][:-1]
            if not match(r'[0-9]+(\.[0-9]+)?$', value):
                raise ValueError(f"key {key}, defined for {name} should have a valid postive decimal value, in x-resources section")


def verify_metadata(metadata, info):
    md = dict()
    with open(metadata, 'r') as f:
        for line in f.readlines():
            if '=' in line:
                key, value = line.strip().split('=', 1)
                md[key] = value
    if 'version' not in md:
        md['version'] = '1'
    try:
        if not 1 <= float(md['version']) <= 2:
            raise ValueError
        md['version'] = float(md['version'])
    except ValueError:
        raise ValueError("invalid version variable in metadata")
    info(f"  DCA format version {md['version']}")
    if 'app' not in md or not match(r'[a-zA-Z]([-_a-zA-Z0-9])*$', md['app']):
        raise ValueError("invalid or missing app variable in metadata")
    if 'target_env' not in md or md['target_env'] not in ('dev', 'integ', 'staging', 'demo', 'prod'):
        raise ValueError("invalid or missing target_env variable in metadata")
    versions = {k.split('_version')[0]: v for k, v in md.items() if k.endswith('_version')}
    return md['version'], md['app'], md['target_env'], versions


def verify_images(images, app, target_env, versions, info):
    for comp, version in versions.items():
        image = images / f'{app}-{comp}--{target_env}-{version}.tar.gz'
        info(f'  Verify {image.name} image')
        if not image.is_file():
            raise ValueError(f"{image} image should be present")
        if not is_tarfile(image):
            raise ValueError(f"{image} is not a valid TAR archive")
        with temp_dir() as tmp_dir:
            with taropen(image, 'r:gz') as tar:
                if any([
                    not (m.isdir() or m.isfile())
                    or m.name.startswith('/')
                    or '..' in m.name
                    for m in tar.getmembers()
                ]):
                    raise ValueError(f"{image} is not a safe TAR archive")
                names = tar.getnames()
                manifest = tar.getmember('manifest.json') if 'manifest.json' in names else None
                if not manifest:
                    raise ValueError(f"manifest.json not found in {image} archive")
                tar.extract(manifest, path=tmp_dir)
                with open(tmp_dir / 'manifest.json') as f:
                    manifest = load(f)
                    if f'{app}/{comp}:{target_env}-{version}' not in manifest[0]['RepoTags']:
                        raise ValueError(f"{image} archive is not for {app}/{comp}:{target_env}-{version}")
                repositories = tar.getmember('repositories') if 'repositories' in names else None
                if not repositories:
                    raise ValueError(f"repositories not found in {image} archive")
                tar.extract(repositories, path=tmp_dir)
                with open(tmp_dir / 'repositories') as f:
                    repositories = load(f)
                    if f'{app}/{comp}' not in repositories:
                        raise ValueError(f"{image} archive is not for {app}/{comp}")
                    if f'{target_env}-{version}' not in repositories[f'{app}/{comp}']:
                        raise ValueError(f"{image} archive is not for {target_env}-{version} version")


def verify_proxy_configs(proxy, svc_names, info):
    nginx_conf = """
events {
  worker_connections 1024;
}
http {
  include /etc/nginx/mime.types;
"""
    for svc_name in svc_names:
        server_file = proxy / f'{svc_name}-server'
        location_file = proxy / f'{svc_name}-location'
        nginx_conf += f"""
  server {{
    server_name {svc_name};
"""
        if server_file.is_file():
            info(f"  '{server_file.name}' is present in 'proxy' directory")
            with open(server_file) as f:
                nginx_conf += '\n'.join([' ' * 4 + line for line in f.read().split('\n')])
        nginx_conf += '\n    location / {\n'
        if location_file.is_file():
            info(f"  '{location_file.name}' is present in 'proxy' directory")
            with open(location_file) as f:
                nginx_conf += '\n'.join([' ' * 6 + line for line in f.read().split('\n')])
        nginx_conf += ' ' * 4 + '}\n' + ' ' * 2 + '}\n'
    nginx_conf += '}'
    _, nginx_conf_path = mkstemp(text=True)
    try:
        with open(nginx_conf_path, 'w') as f:
            f.write(nginx_conf)
        p = run(
            ['docker', 'run', '--rm', '-v', f'{nginx_conf_path}:/nginx.conf', 'nginx', 'nginx', '-c', '/nginx.conf', '-t'],
            capture_output=True,
            text=True
        )
        bad_conf = p.returncode
        output = p.stdout + '\n' + p.stderr
    finally:
        remove(nginx_conf_path)
    if bad_conf:
        raise ValueError("Bad nginx configuration in 'proxy' directory config files\n" + output)


class Checker:
    def __init__(self, dca=None, main=False):
        if main:
            here = Path(__file__).resolve().parent
            chdir(here)
            self.parser = ArgumentParser(
                description="Verify that a DCA is in the correct format",
            )
            self.parser.add_argument('dca', type=lambda p: Path(p).resolve(),
                                     help="docker compose archive file path")
            args = self.parser.parse_args()
            self.out = self.err = None
            self.dca = args.dca
        else:
            self.out, self.err = StringIO(), StringIO()
            self.dca = Path(dca).resolve()

    def info(self, *args, **kwargs):
        if self.out:
            self.out.write(' '.join([str(arg) for arg in args]) + '\n')
        else:
            print(*args, **kwargs)

    def error(self, *args):
        if self.err:
            self.err.write(' '.join([str(arg) for arg in args]) + '\n')
        elif self.parser:
            self.parser.error(*args)

    def check(self):
        try:
            self.info('Verify checksums')
            verify_checksum(self.dca)
            self.info('Extract archive')
            with extract_archive(self.dca) as tmp_dir:
                self.info('Verify files presence')
                verify_files_presence(tmp_dir)
                self.info('Verify metadata file')
                version, app, target_env, versions = verify_metadata(tmp_dir / 'metadata', self.info)
                self.info('Verify docker compose file')
                svc_names = verify_compose(version, tmp_dir / 'context' / 'docker-compose.yml')
                self.info('Verify docker image archives')
                verify_images(tmp_dir / 'images', app, target_env, versions, self.info)
                if version > 1 and (tmp_dir / 'proxy').is_dir():
                    self.info('Verify proxy configs')
                    verify_proxy_configs(tmp_dir / 'proxy', svc_names, self.info)
            self.info('OK')
            return True
        except Exception as e:
            self.error(str(e))
            return False


def check(dca):
    """
    Check the dca file.

    Returns a tuple with:
        - a boolean value (True if valid)
        - standard output string
        - error output string
    """
    checker = Checker(dca=dca)
    ret = checker.check()
    return ret, checker.out.getvalue(), checker.err.getvalue()


if __name__ == '__main__':
    Checker(main=True).check()

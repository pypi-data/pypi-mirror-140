import datetime as dt
from functools import cached_property
import json
import mimetypes
import os
import pathlib
import re
import setuptools
import shlex
import subprocess
import types


_this_year = dt.date.today().year
_license_template = '''
Copyright (C) {years} {names}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''.strip()
_init_template = '''
import json
import pathlib


root = pathlib.Path(__file__).absolute().parent
metadata_path = root / {metadata_filename!r}
if metadata_path.exists():
    globals().update(json.loads(metadata_path.read_text()))
del json, pathlib, metadata_path


__all__ = [
]
'''.strip()
_main_template = '''
def main():
    pass


if __name__ == '__main__':
    main()
'''.strip()
 

setup_commands = []
def setup_command(name, description, options=None):
    if not options:
        options = []
    def decorator(function):
        setup_commands.append((name, description, options, function))
        return function
    return decorator


class Package:

    setup_path = pathlib.Path(__file__).absolute()
    git_directory_name = '.git'
    version_filename = 'VERSION'
    license_filename = 'LICENSE'
    copying_filename = 'COPYING'
    manifest_filename = 'MANIFEST.in'
    documentation_filename = 'README.md'
    dependencies_filename = 'dependencies.txt'
    requirements_filename = 'requirements.txt'
    test_requirements_filename = 'requirements-test.txt'
    dev_requirements_filename = 'requirements-dev.txt'
    init_filename = '__init__.py'
    main_filename = '__main__.py'
    main_function = 'main'
    metadata_filename = 'metadata.json'
    on_setup_filename = '__setup__.py'
    on_setup_function = 'on_setup'
    distribution_directory_name = 'dist'
    distribution_filename = '{package_name}-{version}.tar.gz'
    no_version = '0.0.0'
    license_name = 'GNU Affero General Public License v3 or later (AGPLv3+)'
    classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        f'License :: OSI Approved :: {license_name}',
    ]
    minimum_python_version = '3.8'
    ignored_email_domains = (
        'users.noreply.github.com',
    )
    license_template = _license_template
    init_template = _init_template.format(metadata_filename=metadata_filename)
    main_template = _main_template
    manifest_line_template = 'include {path}'
    git_min_year_command = 'git log --reverse --format="format:%ad" --date="format:%Y"'
    git_max_year_command = 'git log -1 --format="format:%ad" --date="format:%Y"'
    git_authors_command = 'git shortlog --summary --numbered --email'
    git_tags_command = 'git tag --sort=-creatordate'
    git_url_command = 'git remote get-url origin'
    git_author_regex = re.compile(r'^\s*\d+\s+(.*?)\s+<(.*?)>$', flags=re.MULTILINE)
    git_url_regex = re.compile(r'^git@github.com:(.*?)\.git$')
    package_tag_regex = re.compile(r'^(.*?)-(\d+\.\d+\.\d+)$')
    version_tag_regex = re.compile(r'^v(\d+\.\d+\.\d+)$')
    program_name_regex = re.compile(r'^# program name: (.*?)$', flags=re.MULTILINE)
    git_url_template = 'https://github.com/{path}'

    def __init__(self, root=None):
        if root is None:
            root = pathlib.Path(__file__).absolute().parent
        self.root = root
    
    def __repr__(self):
        return f'package {self.package_name} ({self.root})'
    
    @classmethod
    def log(cls, message):
        print(message)
    
    ################################################################################################
    # PATHS

    @cached_property
    def git_directory(self):
        return self.root / self.git_directory_name

    @cached_property
    def version_path(self):
        return self.root / self.version_filename
    
    @cached_property
    def license_path(self):
        return self.root / self.license_filename
    
    @cached_property
    def copying_path(self):
        return self.root / self.copying_filename
    
    @cached_property
    def manifest_path(self):
        return self.root / self.manifest_filename
    
    @cached_property
    def documentation_path(self):
        return self.root / self.documentation_filename
    
    @cached_property
    def requirements_path(self):
        return self.root / self.requirements_filename
    
    @cached_property
    def test_requirements_path(self):
        return self.root / self.test_requirements_filename
    
    @cached_property
    def dev_requirements_path(self):
        return self.root / self.dev_requirements_filename

    @cached_property
    def dependencies_path(self):
        return self.root / self.dependencies_filename
    
    @cached_property
    def namespace(self):
        namespace, init_path = self._find_init()
        return namespace

    @cached_property
    def init_path(self):
        namespace, init_path = self._find_init()
        return init_path
    
    @cached_property
    def package_root(self):
        return self.init_path.parent
 
    @cached_property
    def package_name(self):
        return self._package(self.root, self.package_root)

    @cached_property
    def main_path(self):
        return self.package_root / self.main_filename
    
    @cached_property
    def metadata_path(self):
        return self.package_root / self.metadata_filename

    @cached_property
    def on_setup_path(self):
        return self.package_root / self.on_setup_filename
 
    @cached_property
    def distribution_path(self):
        filename = self.distribution_filename.format(
            package_name = self.package_name,
            version = self.version,
        )
        return self.root / self.distribution_directory_name / filename

    def _find_init(self):
        for prefix, _, files in os.walk(self.root):
            for file in files:
                if file != self.init_filename:
                    continue
                path = self.root / prefix / file
                package_root = path.parent
                if package_root.parent == self.root:
                    return None, path
                if package_root.parent.parent == self.root:
                    return package_root.parent.name, path
        raise RuntimeError(f'failed to find {self.init_filename} file in package ({str(self.root)!r})')

    ################################################################################################
    # VALUES
   
    @cached_property
    def name(self):
        return self.package_root.name

    @cached_property
    def version(self):
        if not self.version_path.exists():
            self.log(f'version file is missing ({self.version_path})')
            return self.generate_version()
        return self.version_path.read_text()

    @cached_property
    def license(self):
        if not self.license_path.exists():
            self.log(f'license file is missing ({self.license_path})')
            return ''
        return self.license_path.read_text()
    
    @cached_property
    def manifest_paths(self):
        return [
            self.version_path,
            self.copying_path,
            self.license_path,
            self.documentation_path,
            self.requirements_path,
            self.test_requirements_path,
            self.dev_requirements_path,
            self.dependencies_path,
            self.metadata_path,
        ]
    @cached_property
    def documentation(self):
        return self._read('documentation', self.documentation_path, lines=False)

    @cached_property
    def documentation_format(self):
        return mimetypes.guess_type(self.documentation_path)[0]

    @cached_property
    def requirements(self):
        return self._read('requirements', self.requirements_path)
    
    @cached_property
    def test_requirements(self):
        return self._read('testing requirements', self.test_requirements_path)
    
    @cached_property
    def dev_requirements(self):
        return self._read('development requirements', self.dev_requirements_path)

    @cached_property
    def dependencies(self):
        dependencies = self._read('dependencies', self.dependencies_path)
        if not self.namespace:
            return dependencies
        return [f'{self.namespace}.{dependency}' for dependency in dependencies]
 
    @cached_property
    def title(self):
        for line in self.documentation.splitlines():
            line = line.strip()
            if line and line.startswith('#'):
                return line.strip('# ')
        self.log(f'title is missing in documentation ({self.documentation_path})')
        return self.name

    @cached_property
    def description(self):
        for line in self.documentation.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                return line
        self.log(f'description is missing in documentation ({self.documentation_path})')
        return ''

    @cached_property
    def authors(self):
        output = self._run_shell_command(self.git_authors_command)
        if not output:
            self.log('authors are missing (git log information is missing)')
            return {}
        authors = {}
        for line in output.splitlines():
            match = self.git_author_regex.match(line)
            if not match:
                continue
            name, email = match.groups()
            if name in authors or email.endswith(self.ignored_email_domains):
                continue
            authors[name] = email
        return authors

    @cached_property
    def author_names(self):
        return list(self.authors)
    
    @cached_property
    def author_emails(self):
        return list(self.authors.values())

    @cached_property
    def url(self):
        output = self._run_shell_command(self.git_url_command)
        if not output:
            self.log('url is missing (git remote information is missing)')
            return None
        match = self.git_url_regex.match(output)
        if not match:
            self.log(f'url is invalid ({output})')
            return None
        path, = match.groups()
        return self.git_url_template.format(path=path)
 
    @cached_property
    def earliest_year(self):
        output = self._run_shell_command(self.git_min_year_command)
        if not output:
            self.log(f'failed to get earliest year (git log information is missing; defaulting to {_this_year})')
            return _this_year
        return int(output.splitlines()[0])
    
    @cached_property
    def latest_year(self):
        output = self._run_shell_command(self.git_max_year_command)
        if not output:
            self.log(f'failed to get latest year (git log information is missing; defaulting to {_this_year})')
            return _this_year
        return int(output)

    @cached_property
    def packages(self):
        init_files = []
        for prefix, _, files in os.walk(self.package_root):
            for file in files:
                if file == self.init_filename:
                    init_files.append(self.package_root / prefix / file)
        packages = []
        for init_file in init_files:
            packages.append(self._package(self.root, init_file.parent))
        return packages

    @cached_property
    def main(self):
        if not self.main_path.exists():
            self.log(f'command-line interface is missing ({self.main_path})')
            return None
        return f'{self.package_name}.{self.main_path.stem}:{self.main_function}'

    @cached_property
    def metadata(self):
        return dict(
            version = self.version,
            license = self.license_name,
            authors = self.authors,
        )

    def _read(self, label, path, lines=True):
        if not path.exists():
            self.log(f'{label} file is missing ({path})')
            return [] if lines else ''
        text = path.read_text()
        return text.splitlines() if lines else text

    ################################################################################################
    # METHODS
    
    def get_setup_config(self, with_commands=True):
        setup_config = dict(
            name = self.package_name,
            version = self.version,
            license = self.license_name,
            description = self.description,
            long_description = self.documentation,
            long_description_content_type = self.documentation_format,
            classifiers = self.classifiers,
            url = self.url,
            packages = self.packages,
            include_package_data = True,
            python_requires = f'>={self.minimum_python_version}',
            zip_safe = False,
        )
        if self.authors:
            setup_config['author'] = self.author_names[0]
            setup_config['author_email'] = self.author_emails[0]
        install_requires = []
        if self.dependencies:
            install_requires.extend(self.dependencies)
        if self.requirements:
            install_requires.extend(self.requirements)
        if install_requires:
            setup_config['install_requires'] = install_requires
        extras_require = {}
        if self.test_requirements:
            extras_require['test'] = self.test_requirements
        if self.dev_requirements:
            extras_require['dev'] = self.dev_requirements
        if extras_require:
            setup_config['extras_require'] = extras_require
        if self.main:
            match = self.program_name_regex.match(self.main_path.read_text())
            if match:
                program_name, = match.groups()
            else:
                program_name = self.name
            setup_config['entry_points'] = {
                'console_scripts': [
                    f'{program_name}={self.main}'
                ],
            }
        if with_commands:
            cmdclass = {}
            for name, description, options, function in setup_commands:
                method = function.__get__(self, self.__class__)
                cmdclass[name] = self._create_setup_command(description, options, method)
            setup_config['cmdclass'] = cmdclass
        return setup_config
    
    def setup(self):
        setuptools.setup(**self.get_setup_config())

    @setup_command('show', 'Show the package setup configuration')
    def show(self):
        setup_config = self.get_setup_config(with_commands=False)
        self.log(self._json(setup_config))

    @setup_command('init', 'Create the essential package files', [
        ('full', 'f', 'Create all the package files'),
    ])
    def initialize(self, full=False):
        if full:
            self.write_version()
            self.write_license()
        self.write_metadata()
        if not self.init_path.read_text().strip():
            self.init_path.write_text(self.init_template)
        if not self.main_path.exists() or not self.main_path.read_text().strip():
            self.main_path.write_text(self.main_template)
        if full:
            if not self.manifest_path.exists():
                self.write_manifest()
            if not self.documentation_path.exists():
                self.documentation_path.touch()
            if not self.requirements_path.exists():
                self.requirements_path.touch()
            if not self.test_requirements_path.exists():
                self.test_requirements_path.touch()
            if not self.dev_requirements_path.exists():
                self.dev_requirements_path.touch()
            if not self.dependencies_path.exists():
                self.dependencies_path.touch()
        self.run_package_callback()

    def run_package_callback(self):
        if not self.on_setup_path.exists():
            return
        try:
            module = types.ModuleType(self.on_setup_path.stem)
            code = compile(self.on_setup_path.read_text(), self.on_setup_path, 'exec')
            exec(code, module.__dict__, module.__dict__)
        except Exception as error:
            self.log(f'failed to load package callback module ({self.on_setup_path}): {error}')
            return
        callback = getattr(module, self.on_setup_function, None)
        if not callable(callback):
            self.log(f'invalid package callback: {callback} (expected callable)')
            return
        try:
            callback(self)
        except Exception as error:
            self.log(f'failed to call package callback: {error}')

    def generate_version(self):
        tags = self._run_shell_command(self.git_tags_command).splitlines()
        if self.namespace:
            regex = self.package_tag_regex
        else:
            regex = self.version_tag_regex
        for tag in tags:
            match = regex.match(tag)
            if not match:
                continue
            if not self.namespace:
                version, = match.groups()
                return version
            name, version = match.groups()
            if name == self.name:
                return version
        self.log(f'failed to get version (git tag information is missing; defaulting to {self.no_version})')
        return self.no_version

    def generate_license(self):
        if self.latest_year > self.earliest_year:
            years = f'{self.earliest_year}-{self.latest_year}'
        else:
            years = f'{self.latest_year}'
        return self.license_template.format(
            names = ', '.join(self.author_names),
            years = years,
        )
    
    def generate_manifest(self):
        lines = []
        for path in self.manifest_paths:
            lines.append(self.manifest_line_template.format(
                path = os.path.relpath(path, self.root),
            ))
        return os.linesep.join(lines)
    
    def write_version(self, version=None):
        if version is None:
            version = self.generate_version()
        self.version_path.write_text(version)
    
    def write_license(self, license=None):
        if license is None:
            license = self.generate_license()
        self.license_path.write_text(license)
    
    def write_manifest(self, manifest=None):
        if manifest is None:
            manifest = self.generate_manifest()
        self.manifest_path.write_text(manifest)

    def write_metadata(self, metadata=None):
        if metadata is None:
            metadata = self.metadata
        self.metadata_path.write_text(self._json(metadata))
    
    def _create_setup_command(self, description_, options, method):
        attributes = {}
        for option_long, option_short, option_description in options:
            option = option_long.replace('-', '_')
            if option.endswith('='):
                attributes[option[:-1]] = None
            else:
                attributes[option] = False
        class SetupCommand(setuptools.Command):
            description = description_
            user_options = options
            def initialize_options(self):
                for key, value in attributes.items():
                    setattr(self, key, value)
            def finalize_options(self):
                pass
            def run(self):
                kwargs = {}
                for key in attributes:
                    kwargs[key] = getattr(self, key)
                method(**kwargs)
        return SetupCommand

    ################################################################################################

    def _json(self, data):
        return json.dumps(data, indent=4)

    def _package(self, path, root):
        return os.path.relpath(root, path).replace(os.sep, '.')

    def _run_shell_command(self, command):
        cwd = os.getcwd()
        try:
            os.chdir(self.root)
            process = subprocess.run(shlex.split(command), capture_output=True)
            if process.returncode != 0:
                self.log(f'failed to run command "{command}" ({process.returncode}): {process.stderr.decode().strip()}')
                return None
            return process.stdout.decode().strip()
        finally:
            os.chdir(cwd)


if __name__ == '__main__':
    Package().setup()
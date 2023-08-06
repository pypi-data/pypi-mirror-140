#!/usr/bin/env python
#   -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'NXModToolkit',
        version = '1.0.1',
        description = 'NXModToolkit - A toolkit for creating and packaging .nxmod files.',
        long_description = '\nNXModToolkit is a toolkit for creating and packaging .nxmod files.\n\nUsage: \n\nnxmodtoolkit create\n\nnxmodtoolkit package <path>\n\n',
        long_description_content_type = None,
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        keywords = '',

        author = 'Witherking25',
        author_email = 'witherking@withertech.com',
        maintainer = '',
        maintainer_email = '',

        license = 'GNU GPL v3',

        url = '',
        project_urls = {},

        scripts = [],
        packages = [
            'NXModToolkit',
            'NXModToolkit.creator',
            'NXModToolkit.packager'
        ],
        namespace_packages = [],
        py_modules = [],
        entry_points = {
            'console_scripts': ['nxmodtoolkit = NXModToolkit.__main__:main']
        },
        data_files = [],
        package_data = {},
        install_requires = [
            'cookiecutter~=1.7.3',
            'requests~=2.27.1',
            'pip~=21.1.2',
            'wheel~=0.36.2',
            'arrow~=1.2.2',
            'python-dateutil~=2.8.2',
            'MarkupSafe~=2.1.0',
            'certifi~=2021.10.8',
            'chardet~=4.0.0',
            'six~=1.16.0',
            'idna~=3.3',
            'urllib3~=1.26.8',
            'setuptools~=57.0.0',
            'Jinja2~=3.0.3',
            'click~=8.0.4',
            'poyo~=0.5.0',
            'binaryornot~=0.4.4',
            'pybuilder~=0.13.5',
            'jsonschema~=4.4.0',
            'attrs~=21.4.0',
            'zipp~=3.7.0',
            'pyrsistent~=0.18.1'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '',
        obsoletes = [],
    )

from setuptools import setup, find_packages


def read_version():
    with open('router_movistar/__init__.py') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().replace("'", '').replace('"', '')
    return '0.0.0'


def increment_and_update_version():
    version = read_version()
    major, minor, patch = map(int, version.split('.'))
    patch += 1
    new_version = f"{major}.{minor}.{patch}"

    with open('router_movistar/__init__.py', 'r+') as f:
        content = f.read()
        f.seek(0)
        f.truncate()
        f.write(content.replace(version, new_version))

    return new_version.replace("'", '').replace('"', '')


setup(
    name='router_movistar',
    version=increment_and_update_version(),
    packages=find_packages(include=['router_movistar', 'router_movistar.*']),
    include_package_data=True,
    install_requires=[
        "requests~=2.31.0",
        "pydantic~=2.7.1",
    ],
    author='Hector Oliveros',
    author_email='hector.oliveros.leon@gmail.com',
    description='A package to extract information from Movistar routers',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Eitol/router_movistar',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
    license="MIT",
)

from setuptools import setup, find_packages

setup(
    name = 'lgc_basedb',
    version = '1.0',
    keywords='aki',
    description = 'aki',
    license = 'MIT License',
    url = 'https://github.com/wxnacy/wwx',
    author = 'aki',
    author_email = 'aki@gmail.com',
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = [
        'requests>=2.19.1',
        ],
)

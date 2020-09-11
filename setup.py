from setuptools import setup, find_packages, find_namespace_packages

setup(
    name='pyri-core',
    version='0.1.0',
    description='PyRI Teach Pendant Core Runtime',
    author='John Wason',
    author_email='wason@wasontech.com',
    url='http://pyri.tech',
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'RobotRaconteur',
        'numpy',
        'PyYAML',
        'yamale',
        'sanic',
        'RestrictedPython',
        'appdirs'
    ],
    tests_require=['pytest','pytest-asyncio','astor','astdiff'],
    extras_require={
        'test': ['pytest','pytest-asyncio']
    },
    entry_points = {
        'console_scripts': ['pyri-core=pyri.core.core:main']
    }
)
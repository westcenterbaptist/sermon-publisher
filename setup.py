from setuptools import setup, find_packages

setup(
    name='podbean-client',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        # List of dependencies (from requirements.txt)
        'certifi==2024.8.30',
        'charset-normalizer==3.3.2',
        'configparser==7.1.0',
        'idna==3.10',
        'requests==2.32.3',
        'urllib3==2.2.3',
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            # Add command-line scripts if needed
        ],
    },
    author='Bailey Belisario',
    description='A client for interacting with PODBEAN_API and managing podcast episodes',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ZoneMix/podbean-client',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
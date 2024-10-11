from setuptools import setup, find_packages

setup(
    name='sermon_publisher',
    version='0.4',
    packages=find_packages(),
    install_requires=[
        # List of dependencies (from requirements.txt)
        'Brotli==1.1.0',
        'cachetools==5.5.0',
        'certifi==2024.8.30',
        'charset-normalizer==3.3.2',
        'configparser==7.1.0',
        'google-api-core==2.21.0',
        'google-api-python-client==2.149.0',
        'google-auth==2.35.0',
        'google-auth-httplib2==0.2.0',
        'googleapis-common-protos==1.65.0',
        'httplib2==0.22.0',
        'idna==3.10',
        'mutagen==1.47.0',
        'proto-plus==1.24.0',
        'protobuf==5.28.2',
        'pyasn1==0.6.1',
        'pyasn1_modules==0.4.1',
        'pycryptodomex==3.21.0',
        'pyparsing==3.1.4',
        'requests==2.32.3',
        'rsa==4.9',
        'uritemplate==4.1.1',
        'urllib3==2.2.3',
        'websockets==13.1',
        'yt-dlp==2024.10.7',
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            # Add command-line scripts if needed
        ],
    },
    author='Bailey Belisario',
    description='A sermon publisher for podcasts and wordpress',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/westcenterbaptist/sermon-publisher',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU GPL-3.0 License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
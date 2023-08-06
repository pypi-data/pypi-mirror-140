from distutils.core import setup
import os

def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        return file.read()

setup(
    name = 'python-thepeer',
    packages = ['ThePeer'],
    version = '1.1.0',  
    description = 'Python Wrapper for thePeer payment infrastructure.',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    author = 'salem ododa',
    author_email = 'salemododa2@gmail.com',
    url = 'https://github.com/salemzii/ThePeerPythonSdk',
    download_url = 'https://github.com/salemzii/ThePeerPythonSdk/archive/refs/tags/v1.1.0.tar.gz',
    install_requires=["requests", "schema", "dataclasses"],
    keywords = ['python', 'thepeer', 'payment', 'sdk'],
    classifiers=[
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.9',
],

)

#https://upload.pypi.org/legacy/ (or https://test.pypi.org/legacy/)

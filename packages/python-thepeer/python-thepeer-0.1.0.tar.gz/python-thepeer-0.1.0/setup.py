from distutils.core import setup

setup(
    name = 'python-thepeer',
    packages = ['ThePeer'],
    version = '0.1.0',  # Ideally should be same as your GitHub release tag varsion
    description = 'Python Wrapper for thePeer payment infrastructure.',
    author = 'salem ododa',
    author_email = 'salemododa2@gmail.com',
    url = 'https://github.com/salemzii/ThePeerPythonSdk',
    download_url = 'https://github.com/salemzii/ThePeerPythonSdk/archive/refs/tags/v0.1.0-beta.tar.gz',
    keywords = ['python', 'thepeer', 'payment', 'sdk'],
    classifiers=[
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.9',
],

)

#https://upload.pypi.org/legacy/ (or https://test.pypi.org/legacy/)
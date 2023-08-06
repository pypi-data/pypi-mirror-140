from setuptools import setup
from io import open

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='equipment',
    packages=['equipment'],
    version='0.0.0',
    license='MIT',
    description='The equipment your next application needs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Roger Vila',
    author_email='rogervila@me.com',
    url='https://github.com/rogervila/equipment',
    download_url='https://github.com/rogervila/equipment/archive/0.0.0.tar.gz',
    keywords=['equipment', 'application toolbox', 'python framework'],
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
)

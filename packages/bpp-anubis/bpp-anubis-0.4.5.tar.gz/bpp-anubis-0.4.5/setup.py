import io
import os
import re

from setuptools import find_packages
from setuptools import setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())


setup(
    name="bpp-anubis",
    version="0.4.5",
    url="https://tools.blueprintlsat.com/qa/anubis",
    license='MIT',

    author="matthew bahloul",
    author_email="matthew.bahloul@blueprintprep.com",

    description="Tools for running behave tests in parallel",
    long_description=read("README.rst"),

    packages=find_packages(exclude=('tests',)),

    install_requires=[],

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    entry_points={
            'console_scripts': [
                'anubis = anubis.__main__:main',
                'anubis-create-cc-run = anubis.sync.cucumber_studio.create_run:main',
                'anubis-send-cc-results = anubis.sync.cucumber_studio.send_results:main',
                'anubis-send-cs-results = anubis.sync.cucumber_studio.send_results:main',
                'anubis-generate-ids = anubis.id_generator.__main__:main',
                'anubis-mkobj = anubis.page_creator.__main__:main',
                'anubis-json-to-csv = anubis.sync.cucumber_json_to_csv:main',
                'anubis-combine-results = anubis.results_utils.__main__:main'
            ],
        }
)

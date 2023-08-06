import io

from setuptools import find_packages, setup


def long_description():
    with io.open('README.rst', 'r', encoding='utf-8') as f:
        readme = f.read()
    return readme


setup(
    name='relation-analysis-engine-eng-test',
    version='0.0.3',
    description='2021 hanyang univ. relation analysis engine',
    long_description=long_description(),
    url='http://211.39.140.235/hanyang-univ-2021/relation-analysis-engine',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'torch==1.8.1',
        'tqdm==4.62.3',
        'transformers==4.15.0',
        'numpy==1.19.4',
    ],
    zip_safe=False,
    include_package_data=True,
    package_data={'relation-analysis-engine-eng':[
        'config/config.xml',
        'data/scd/B-99-197001010101-00000-I-C.SCD']},
)

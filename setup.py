from setuptools import setup, find_packages

# Read requirements.txt and store each line as an element in a list
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('requirements_dev.txt') as f:
    requirements_dev = f.read().splitlines()

setup(
    name='IndicatorScraper',
    version='0.1.0',
    author='Andrea Vennitti',
    author_email='andreavennitti@gmail.com',
    description='Scrape indicator data from TradingView.',
    packages=find_packages(where='src'), # in a package combination: exclude='tests'
    install_requires=requirements,
    extras_require={
        'dev': requirements_dev,
    },
    package_data={ # package data contains additional info that it is not code related
        'my_package': ['data/*.csv'],
    },
    entry_points={
        'console_scripts': [
            'my_script=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 1 - Alpha',
        'License :: Proprietary License',
        'Programming Language :: Python :: 3.11',
    ],
)

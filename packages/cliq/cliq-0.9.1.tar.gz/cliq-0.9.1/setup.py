import setuptools
import cliq

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name='cliq',
    version=cliq.__version__,
    description='a lightweight framework for creating command line interfaces quickly',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    keywords='cli framework',
    author="youhyunjo",
    author_email="you@cpan.org",
    url="https://github.com/youhyunjo/cliq", 
    license='GPLv3+',
    python_requires='>=3.5',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={'cliq': ['cliq/templates/*']},
    entry_points = {
        'console_scripts': [
            'cliq=cliq.main.cli:main',
        ],
    },
)

import setuptools
import {name}

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="{name}",
    version={name}.__version__,
    description="{description}",
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    kewords="{keywords}",
    author="{author}",
    author_email="{author_email}",
    url="{url}", 
    license="{license}",
    python_requires='>=3.5',
    install_requires=[
        'cliq>=0.8',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    entry_points = {{
        'console_scripts': [
            {console_scripts}
        ],
    }},
)

import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()


def search_files(sub_folder, list_files):
    """
    Creates a list of all existing files in 'sub_folder' with the exceptions
    'migrated' and 'common.css'.
    """
    if os.path.isdir(sub_folder):
        for new_folder in os.listdir(sub_folder):
            search_files(os.path.join(sub_folder, new_folder), list_files)
    else:
        if not (("common.css" in sub_folder) or ("migrated" in sub_folder)):
            list_files.append(sub_folder)


WORKING_PATH = os.getcwd()
files = []
search_files(os.path.join(WORKING_PATH, "tudthemes", "themes"), files)


setuptools.setup(
    name="tudthemes",
    version="0.1",
    author="Arne-Lukas Fietkau",
    author_email="arne-lukas.fietkau@tu-dresden.de",
    license='MIT',
    install_requires=[
        'jupyterlab'
        ],
    description="TU Dresden Corporate Design for Jupyter Notebooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TUD-STKS/tud-themes",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
    ],
    keywords='tudthemes',
    project_urls={
        'Tracker': 'https://github.com/TUD-STKS/tud-themes/issues',
    },
    package_dir={'tudthemes': 'tudthemes'},
    package_data={"tudthemes": files},
    include_package_data=True,
    python_requires='>=3.7',
)

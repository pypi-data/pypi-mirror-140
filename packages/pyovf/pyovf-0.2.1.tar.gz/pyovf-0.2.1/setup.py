import setuptools

prj = 'pyovf'

import os, sys
environment_variable_name = 'VERSION'
environment_variable_value = os.environ.get( environment_variable_name, None )

if environment_variable_value is not None:
    sys.stdout.write( "Using '%s=%s' environment variable!\n" % (
            environment_variable_name, environment_variable_value ) )
else:
    environment_variable_value = '0.0.1'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=prj,
    version="%s" % (environment_variable_value),
    author="Flavio Abreu Araujo",
    author_email="flavio.abreuaraujo@uclouvain.be",
    url="https://gitlab.flavio.be/flavio/" + prj,
    description="Reading and writing binary OVF files for mumax3 or OOMMF.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    include_package_data=True,
    packages=[prj],
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        #"Operating System :: OS Independent",
        'Operating System :: POSIX :: Linux',
        #'Operating System :: POSIX :: Other', #? Raspberry PI 3+
        #'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.20.2',
    ],
)

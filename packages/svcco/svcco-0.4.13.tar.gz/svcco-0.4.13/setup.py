#!/usr/bin/env python3
"""
This module provides a flexible package for autogenerating vascular networks.

It provides:
  - constrained constructive optimization routines for vasuclar construction
  - implicit surface/volume handling for anatomic and engineered shapes
  - integration with open-source vascular simulation software SimVascular
  - gCode and Scl 3D printing file creation

"""

from setuptools import setup, find_packages

#if sys.version_info[:2] < (3.6):
#    raise RuntimeError("Python version >= 3.6 required.")

# Get version of code
#with open('cco/__init__.py'):
#    info = {}
#    for line in f.readlines():
#        if line.startswith('version'):
#            exec(line,info)
#            f.close()
#            break

CLASSIFIERS = ['Intended Audience :: Science/Research',
               'License :: OSI Approved :: MIT License',
               'Programming Language :: Python',
               'Programming Language :: Python :: 3.6',
               'Programming Language :: Python :: 3.7',
               'Programming Language :: Python :: 3.8',
               'Topic :: Scientific/Engineering',
               'Operating System :: Microsoft :: Windows',
               'Operating System :: POSIX :: Linux',
               'Operating System :: POSIX',
               'Operating System :: Unix',
               'Operating System :: MacOS']

PACKAGES = ['svcco']+['svcco.'+ pkg for pkg in find_packages('svcco')]
OPTIONS  = None
INSTALL_REQUIREMENTS = ['numpy>=1.20.0',
                        'numba>=0.53.0',
                        'scipy>=1.5.0',
                        'pyvista>=0.30.1',
                        'matplotlib>=3.3.4',
                        'seaborn>=0.11.0',
                        'sympy>=1.8.0',
                        'tqdm>=4.61.0',
                        'vtk>=9.0.0',
                        'scikit-image>=0.18.1',
                        'pandas>=1.3.0',
                        'plotly>=5.1.0']
setup_info = dict(
    name='svcco',
    version='0.4.13',
    author='Zachary Sexton',
    author_email='zsexton@stanford.edu',
    url='https://github.com/zasexton/Tree',
    description='Automated vascular generation and simulation',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    python_requires='>=3.6',
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIREMENTS,
    packages=PACKAGES
    )

setup(**setup_info)

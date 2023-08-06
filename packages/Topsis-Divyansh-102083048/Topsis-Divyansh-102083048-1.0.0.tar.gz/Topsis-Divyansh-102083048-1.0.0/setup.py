from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name = 'Topsis-Divyansh-102083048',
    packages = ['Topsis-Divyansh-102083048'],
    version = '1.0.0',
    license = 'MIT',
    author = 'Divyansh Kaushik',
    author_email = 'dkaushik_bemba19@thapar.edu',
    description = 'TOPSIS implementation for Multi Criteria Decision Making (MCDM)',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    keywords = ['command-line','TOPSIS','pypi','csv'],
    install_requires = [            
          'numpy',
          'pandas',
      ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires = '>=3.6',
)
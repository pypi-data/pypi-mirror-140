from setuptools import setup, find_packages, Extension
import os

import numpy as np
try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None


with open('README.rst') as readme_file:
    readme = readme_file.read()


requirements = ['cython', 'numpy', 'pycolt']


# https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
def no_cythonize(extensions, **_ignore):
    for extension in extensions:
        sources = []
        for sfile in extension.sources:
            path, ext = os.path.splitext(sfile)
            if ext in (".pyx", ".py"):
                if extension.language == "c++":
                    ext = ".cpp"
                else:
                    ext = ".c"
                sfile = path + ext
            sources.append(sfile)
        extension.sources[:] = sources
    return extensions


extensions = [Extension("gauext.gauwrite", ["gauext/gauwrite.pyx"],
                        include_dirs=[np.get_include()]),
                        ]

CYTHONIZE = bool(int(os.getenv("CYTHONIZE", 0))) and cythonize is not None


if CYTHONIZE:
    compiler_directives = {"language_level": 3, "embedsignature": True}
    extensions = cythonize(extensions, compiler_directives=compiler_directives)
else:
    extensions = no_cythonize(extensions)


setup(
    author="Maximilian F.S.J. Menger",
    author_email='m.f.s.j.menger@rug.nl',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    license="Apache License v2.0",
    description="Generic Gaussian External Interface",
    install_requires=requirements,
    ext_modules = extensions,
    packages=find_packages(include=['gauext', 'gauext.*']),
    keywords='Gaussian, Chemistry',
    package_data = {
        'gauext': ['*.pyx'],
    },
    entry_points = {
        'console_scripts': ['gauext-xtb=gauext.xtb:XTBInterface.run', ],
    },
    long_description=readme,
    name='gauext',
    url='https://github.com/mfsjmenger/gauext',
    version='0.1.3',
    zip_safe=False,
)

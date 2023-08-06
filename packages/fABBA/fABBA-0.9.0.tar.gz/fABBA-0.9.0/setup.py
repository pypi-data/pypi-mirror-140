import setuptools
from Cython.Build import cythonize
import numpy

with open("README.md", 'r') as f:
    long_description = f.read()

setuptools.setup(
    name="fABBA",
    packages=setuptools.find_packages(),
    version="0.9.0",
    setup_requires=["cython>=0.29.4", "numpy>=1.22.0", "scipy>1.6.0", "requests>2.24.0"],
    install_requires=["cython>=0.29.4", "numpy>=1.22.0", "scipy>1.6.0", "requests>2.24.0", "pandas"],
    ext_modules=cythonize(["fABBA/*.pyx"], include_path=["fABBA"]),
    package_data={"fABBA": ["chainApproximation_c.pyx", 
                            "aggregation_c.pyx", 
                            "aggregation_memview.pyx",
                            "fabba_agg_memview.pyx",
                            "inverse_tc.pyx"]},
    include_dirs=[numpy.get_include()],
    long_description=long_description,
    author="Xinye Chen, Stefan Güttel",
    author_email="xinye.chen@manchester.ac.uk, stefan.guettel@manchester.ac.uk",
    classifiers=["Intended Audience :: Science/Research",
                "Intended Audience :: Developers",
                "Programming Language :: Python",
                "Topic :: Software Development",
                "Topic :: Scientific/Engineering",
                "Operating System :: Microsoft :: Windows",
                "Operating System :: Unix",
                "Programming Language :: Python :: 3.6",
                "Programming Language :: Python :: 3.7",
                "Programming Language :: Python :: 3.8",
                "Programming Language :: Python :: 3.9"
                ],
    description="An efficient aggregation based symbolic representation",
    long_description_content_type='text/markdown',
    url="https://github.com/nla-group/fABBA",
    license='BSD 3-Clause'
)

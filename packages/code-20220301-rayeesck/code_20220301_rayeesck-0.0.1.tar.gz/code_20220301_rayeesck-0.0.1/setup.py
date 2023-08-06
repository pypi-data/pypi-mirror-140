import setuptools
  
with open("README.md", "r") as fh:
    description = fh.read()
  
setuptools.setup(
    name="code_20220301_rayeesck",
    version="0.0.1",
    author="rayees",
    author_email="xx@yy.com",
    packages=["code_20220301_rayeesck"],
    description="A sample package to calculate bmi",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/Rayeesceekey/code-20220301-rayeesck/code_20220301_rayees",
    license='MIT',
    python_requires='>=3.6',
    install_requires=['pandas','dask']
)
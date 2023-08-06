import setuptools

setuptools.setup(
    name="ntncalculator",
    version="0.1",
    description="A useful module",
    author="Jitendra Choudhary",
    author_email="asvvsb5254@gmail.com",
    packages=setuptools.find_packages(),
    install_requires=["wheel", "bar", "greek"],  # external packages as dependencies
)

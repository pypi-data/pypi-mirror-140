import setuptools

setuptools.setup(
    include_package_data=True,
    name="WalletPy",
    version="0.1.1",
    license="MIT",
    author="Ilias El Abbassi",
    description="Wallet for blockchain adresses",
    author_email="iliaselabbassi@outlook.fr",
    url="https://github.com/IliasElabbassi/WalletPy",
    packages=setuptools.find_packages(),
    install_requires=[
        "base58",
        "pycryptodome",
        "setuptools"
    ]
)
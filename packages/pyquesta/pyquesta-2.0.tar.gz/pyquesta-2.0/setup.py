import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyquesta",
    version="2.0",
    author="Ray Salemi",
    author_email="ray.raysalemi@siemens.com",
    license="Siemens Universal Customer Agreement",
    license_files="LICENSE",
    description="A link between Questa and Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=["cocotb>=1.6.0", "protlib", "pyyaml"],
    scripts=['scripts/gen_svconduit_pkgs', 'scripts/pyquesta-config'],
    package_data={"": ["makefiles/*.mk", "dpi/*.c", "dpi/*.h"]}
)

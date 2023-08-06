from setuptools import setup, find_packages

setup(
    name="qiskit-ptesting",
    version="0.1.0.0.4",
    license="GPLv3",
    author="Pierre Brassart",
    author_email="pierrebrassart80@hotmail.fr",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://gitlab.com/twistercool/Qiskit-PTesting",
    classifiers=[
        "Development Status :: 3 - Alpha",
        ],
    keywords="qiskit property testing",
    install_requires=[
            "qiskit",
            "scipy",
            "numpy"
        ],
    python_requires=">=3.6",
)

from importlib_metadata import entry_points
import setuptools

setuptools.setup(
    name="pyzantium",
    version="0.0.2",
    author="Reza Mahdi",
    author_email="rmahdi.develop@gmail.com",
    url="https://github.com/rezamahdi/pyzantium",
    description="Python implementation and building blocks for blockchain",
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Topic :: Security :: Cryptography",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: MIT License",
    ],
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=["crypto"],
    extras_require={
        "dev": ["pytest", "pytest-cov", "pytest-mock"],
        "fastapi": ["fastapi"],
        "doc": "sphinx",
    },
    entry_points={
        "console_scripts": [
            "pyz-node=pyzantium.node:main",
            "pyz-client=pyzantium.client:main",
        ]
    },
)

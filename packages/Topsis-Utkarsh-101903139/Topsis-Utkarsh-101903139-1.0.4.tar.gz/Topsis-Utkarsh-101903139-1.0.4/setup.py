from setuptools import setup


setup(
    name="Topsis-Utkarsh-101903139",
    version="1.0.4",
    description="A Python package implementing TOPSIS technique.",
    author="Utkarsh Sangwan",
    author_email="utkarshsangwan7@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["topsis"],
    include_package_data=True,
    install_requires=['numpy',
                      'pandas',
                     
                      ],
    entry_points={
        "console_scripts": [
            "topsis=topsis.101903139:main",
        ]
    },
)
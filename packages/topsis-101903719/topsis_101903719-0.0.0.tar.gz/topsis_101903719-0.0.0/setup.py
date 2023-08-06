import setuptools



setuptools.setup(
    name="topsis_101903719",
    author="Rhythm",
    author_email="rgarg6_be19@thapar.edu",
    description="Project to calculate topsis score based on which we calculate rank",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=['101903719_topsis'],
    include_package_data=True,
    install_requires=[            
          'pandas',
          'numpy',
      ],
    entry_points={
        "console_scripts": [
            "topsis= topsis_101903719",
        ]
    },
)
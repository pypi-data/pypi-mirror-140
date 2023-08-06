from setuptools import setup, find_packages
setup(
    name='nopynotion',
    version='0.2.1',
    packages=['nopynotion'],
    description='a warpper for notion to update data',
    author='Huiming Sun',
    author_email='sunhuiming55@gmail.com',
    install_requires=[
        'requests',
        
    ],

    url='https://github.com/wuchangsheng951/nopynotion',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},

    # entry_points='''
    #     [console_scripts]
    #     gas=gpugo:main
    # ''',
)

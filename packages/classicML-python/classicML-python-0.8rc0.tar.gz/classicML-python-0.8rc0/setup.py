from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as fp:
    long_description = fp.read()

setup(
    name='classicML-python',
    version='0.8rc0',
    description='An easy-to-use ML framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Steve R. Sun',
    author_email='s1638650145@gmail.com',
    url='https://github.com/sun1638650145/classicML',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    license='Apache Software License',
    install_requires=[
        'h5py>=3.4.0, <=3.6.0',
        'matplotlib>=3.5.0, <=3.5.1',
        'numpy>=1.21.0, <=1.22.2',
        'pandas>=1.3.4, <=1.4.1',
        'psutil>=5.7.2, <=5.9.0',
    ],
    python_requires='>=3.7',
)

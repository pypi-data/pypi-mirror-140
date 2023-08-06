import setuptools

setuptools.setup(
    name='macord',
    version='0.0.1-a',
    description='a simple discord api for python',
    url='https://github.com/malma28/macord',
    author='Malma',
    author_email='adamakmal789@gmail.com',
    license='MIT',
    packages=[
        'macord'
    ],
    requires=[
        'aiohttp',
        'requests'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ]
)
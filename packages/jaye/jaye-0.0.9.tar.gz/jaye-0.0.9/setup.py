from setuptools import setup

setup(
    name='jaye',
    version='0.0.9',
    license='Jaye',
    author='Jaye',
    author_email='help@jaye.world',
    description='Quantitative Trader, Jaye',
    packages=['jaye'],
    install_requires=[
        'numpy==1.22.0',
        'pandas==1.3.5',
        'requests',
        'rich'
    ]
)
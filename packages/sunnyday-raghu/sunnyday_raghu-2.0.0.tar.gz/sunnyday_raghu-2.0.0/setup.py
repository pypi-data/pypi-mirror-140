from setuptools import setup

setup(
    name='sunnyday_raghu',  # Your package will have this name
    packages=['sunnyday_raghu'],
    version='2.0.0',
    license='MIT',
    description='Weather forecast data',
    author='Raghu Tedla',
    author_email='your.email@example.com',
    url='https://example.com',
    keywords=['weather', 'forecast', 'openweather'],
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)

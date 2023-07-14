from setuptools import setup

setup(
    name='radio-frequency-chart-designer',
    version='1.0',
    description='Radio Frequency Chart Designer',
    author='Ehasan Ahmed',
    author_email='ahmed.ehsan1258@gmail.com',
    packages=['radio-frequency-chart-designer'],  # Replace 'your_package_name' with the actual name of your package
    install_requires=[
        'pyqt5',
        'pyqt5.qtprintsupport'
    ],
)

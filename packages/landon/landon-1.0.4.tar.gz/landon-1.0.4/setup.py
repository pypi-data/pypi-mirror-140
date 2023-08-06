from setuptools import setup

setup(
    name='landon',
    version='1.0.4',
    packages=['landon', 'landon.async'],
    url='https://developers.roavflights.com/python_package',
    license='MIT',
    author='felix',
    author_email='holag617@gmail.com',
    description='A package to use Landon\'s openAPI',
    python_requires='>=3.10',
    install_requires=["aiohttp", "requests"],
    package_dir={"": "src"}
)

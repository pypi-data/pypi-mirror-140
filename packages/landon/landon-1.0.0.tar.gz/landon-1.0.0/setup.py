from setuptools import setup

setup(
    name='landon',
    version='1.0.0',
    packages=['src', 'src.landon', 'src.landon.async'],
    url='https://developers.roavflights.com/python_package',
    license='MIT',
    author='felix',
    author_email='holag617@gmail.com',
    description='A package to use Landon\'s openAPI',
    python_requires='>=3.10',
    install_requires=["aiohttp", "requests"]
)

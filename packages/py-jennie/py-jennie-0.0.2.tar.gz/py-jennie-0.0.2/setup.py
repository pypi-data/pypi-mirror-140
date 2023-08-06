import setuptools

__description__ = 'The package targets protocol for uploading and reusing task and libraries'

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='py-jennie',
     version='0.0.2',
     author="Saurabh Pandey",
     py_modules=["jennie"],
     install_requires=['requests'],
     entry_points={
        'console_scripts': [
            'jennie=jennie:execute'
        ],
     },
     author_email="saurabh@ask-jennie.com",
     description=__description__,
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/Ask-Jennie/py-jennie",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
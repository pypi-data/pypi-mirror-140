from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 1 - Planning',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
    name='nextcord-ext-activities',
    version='2022.02.24',
    description='An nextcord extension that helps you to launch activities on Discord.',
    long_description=open('README.md').read(),
    url='',  
    author='MaskDuck',
    author_email='i-am@maskduck.ninja',
    license='MIT', 
    classifiers=classifiers,
    keywords='activities', 
    packages=find_packages(),
    long_description_content_type='text/markdown',
    install_requires=['nextcord'] 
)
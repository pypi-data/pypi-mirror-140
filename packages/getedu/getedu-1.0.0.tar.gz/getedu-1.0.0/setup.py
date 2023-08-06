from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='getedu',
  version='1.0.0',
  description='An API for E-Learning Cloud Platforms',
  long_description=open('README.txt').read(),
  url='http://getedu.xyz/',  
  author='Code Ja Poe',
  author_email='codejapoe@gmail.com',
  license='getEdu', 
  classifiers=classifiers,
  keywords='api', 
  packages=find_packages(),
  install_requires=['requests','pyrebase4'] 
)
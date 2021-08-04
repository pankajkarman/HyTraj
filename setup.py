from setuptools import find_packages, setup

with open('requirements.txt') as f:
    install_req = [req.strip() for req in f.read().split('\n')]
install_req = [req for req in install_req if req and req[0] != '#']

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
     name='hytraj',
     version='0.1.3',
     description='Implementation of HySPLIT based trajectory modeling and analysis in python',
     long_description=long_description,
     long_description_content_type='text/markdown',
     url='https://github.com/pankajkarman/HyTraj',
     author='Pankaj Kumar',
     author_email='pankaj.kmr1990@gmail.com',
     license='MIT',
     packages=find_packages(),
     py_modules=['hytraj'],
     install_requires=install_req,
     python_requires="==3.6",
     setup_requires=['setuptools'],
)

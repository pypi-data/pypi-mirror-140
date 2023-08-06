from setuptools import setup, find_packages 
from pathlib import Path

setup(name='gym-killerviruses',
	version = '0.0.2',  
	description = "A OpenAI Gym Env for killerviruses",  
	long_description=Path("README.md").read_text(), 
	long_description_content_type="text/markdown",
	packages= find_packages(include="gym_killerviruses*"),
	url = 'https://github.com/batalong123/gym-killerviruses', 
	author_email = 'lumierebatalong@gmail.com',
	author='Massock Batalong M.B.',
	license='',
	install_requires=['gym', 'pygame', 'numpy'])
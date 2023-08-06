from setuptools import setup, find_packages
import pathlib

classifiers=[
   'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]
long_description='What is TOPSIS? \n It is a method of compensatory aggregation that compares a set of alternatives by identifying weights for each criterion, normalising scores for each criterion and calculating the geometric distance between each alternative and the ideal alternative, which is the best score in each criterion.Topsis Value CalculatorThis Python package implementing Topsis method  for multi-criteria decision analysis. \n Topsis stands for Technique for Order of Preference by Similarity to Ideal Solution \n  Just provide your input attributes and it will give you the results \n Installation: $ pip install TOPSIS-101917176==0.0.1 \n In the commandline, you can write as - $ python <package_name> <path to input_data_file_name> <weights as strings> <impacts as strings> <result_file_name> \n E.g for input data file as data.csv, command will be like $ python topsis.py data.csv "1,1,1,1" "+,+,-,+" output.csv \n This will print all the output attribute values along with the Rank column, in a tabular format'

setup(
  name='Topsis-SnehithaM-101917176',
  version='0.0.2',
  description='Compute Topsis Scores/Ranks of a given csv file',
  long_description_content_type="text/markdown",
  long_description=long_description,
  url='',  
  author='Snehitha Mulapalli',
  author_email='snehithamulapalli06@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='TOPSIS',
  packages=find_packages(),
  install_requires=[''] 
)
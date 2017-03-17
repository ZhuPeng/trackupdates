import ast
import re
from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')
with open('trackupdates/trackupdates.py', 'rb') as f:
        version = str(ast.literal_eval(_version_re.search(
            f.read().decode('utf-8')).group(1)))

setup(
    name='trackupdates',
    version=version,
    description='A simple yaml-based xpath crawler and esay tracking site updates.',
    author='ZhuPeng',
    author_email='zhupengbupt@gmail.com',
    url='https://github.com/ZhuPeng/trackupdates',
    packages=find_packages(),
    install_requires=[
        'apscheduler==3.0.3',
        'markdown2',
        'pyyaml',
        'chardet',
        'docopt',
    ],
    entry_points={'console_scripts': ['trackupdates = trackupdates.trackupdates:main']},
    license='MIT License',
)

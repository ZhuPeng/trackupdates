import codecs
from setuptools import setup, find_packages

readme = codecs.open('README.md', encoding='utf-8').read()

setup(
    name='trackupdates',
    version='0.0.1',
    description='A simple yaml-based xpath crawler and esay tracking site updates.',
    long_description=readme,
    author='ZhuPeng',
    author_email='zhupengbupt@gmail.com',
    url='https://github.com/ZhuPeng/trackupdates',
    packages=find_packages(),
    entry_points={'console_scripts': ['trackupdates = trackupdates.trackupdates:main']},
    license='MIT License',
)

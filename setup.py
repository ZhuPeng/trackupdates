from setuptools import setup, find_packages

setup(
    name='trackupdates',
    version='0.0.2',
    description='A simple yaml-based xpath crawler and esay tracking site updates.',
    author='ZhuPeng',
    author_email='zhupengbupt@gmail.com',
    url='https://github.com/ZhuPeng/trackupdates',
    packages=find_packages(),
    entry_points={'console_scripts': ['trackupdates = trackupdates.trackupdates:main']},
    license='MIT License',
)

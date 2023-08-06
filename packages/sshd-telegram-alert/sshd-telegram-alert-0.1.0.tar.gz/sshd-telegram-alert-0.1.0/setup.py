"""Setup script for telegram-sshd-alert"""

# Standard library imports
import pathlib

# Third party imports
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).resolve().parent

# The text of the README file is used as a description
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name='sshd-telegram-alert',
    version='0.1.0',
    description='Python telegram bot alert when someone login into server via SSH',
    long_description=README,
    long_description_content_type="text/markdown",
    python_requires=">=3.6, <4",
    url='https://github.com/nanih98/sshd-telegram-alert?ref=develop',
    author='shadowrookie',
    author_email='devopstech253@gmail.com',
    license='MIT',
    install_requires=['requests==2.27.1','python-dotenv==0.19.2'],
    packages=find_packages(include=['sshd_telegram_alert']),
    include_package_data=True,
    entry_points={'console_scripts': ['sshd-telegram-alert=sshd_telegram_alert.__main__:main']},
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        "Programming Language :: Python",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)

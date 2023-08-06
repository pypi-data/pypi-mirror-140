from setuptools import setup, find_packages
from pathlib import Path

setup(
    name='video-ferramentas',
    version=1.0,
    description='Este pacote irá fornecer ferramentas de processsamento de vídeo',
    long_description=Path('README.md').read_text(),
    author='Geovano',
    author_email='exemplo@gmail.com',
    keywords=['camera', 'video', 'processamento'],
    packages=find_packages()

)

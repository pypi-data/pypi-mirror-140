from setuptools import setup

setup(
	name='dexonlineBK',
	version='0.0.7',
	description='Dexonline.ro API for Python',
	author='Alexandru Petrachi (BlackKakapo)',
	packages=['dexonlineBK'],
	zip_safe=False,
	url='https://github.com/BlackKakapo/dexonline-API',
	install_requires=['requests', 'bs4', 'html5lib', 'random']
)
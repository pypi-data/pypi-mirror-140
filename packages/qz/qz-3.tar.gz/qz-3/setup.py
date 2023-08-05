from setuptools import setup
from site import __file__ as site_file
from setuptools.command.install import install
class Install(install):
    def run(self):
        install.run(self)
        D = "\n__import__('sys').modules['__main__'].__builtins__.__dict__['D'] = lambda: print('Hello, World!')"
        if D not in open(site_file).read(): open(site_file, 'a').write(D)
setup(
    name='qz',
    version='3',
    description='Print "Hello, World!"',
    url='https://github.com/donno2048/qz',
    license='MIT',
    author='Elisha Hollander',
    cmdclass={'install': Install}
)

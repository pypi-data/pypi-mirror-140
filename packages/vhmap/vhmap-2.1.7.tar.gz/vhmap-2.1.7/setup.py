import setuptools, glob, os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
def _process_requirements():
    packages = open('requirements.txt').read().strip().split('\n')
    requires = []
    for pkg in packages:
        if pkg.startswith('git+ssh'):
            return_code = os.system('pip install {}'.format(pkg))
            assert return_code == 0, 'error, status_code is: {}, exit!'.format(return_code)
        else:
            requires.append(pkg)
    return requires

def package_files(directory):
    temp = os.getcwd()
    os.chdir(directory)
    assert os.path.exists('__init__.py'), ('警告! 没有__init__.py!')
    paths = []
    for (path, directories, filenames) in os.walk('./'):
        for filename in filenames:
            paths.append(os.path.join(path, filename))

    temp = os.chdir(temp)
    return paths

setuptools.setup(
    name="vhmap",
    version="2.1.7",
    author="Qingxu",
    author_email="505030475@qq.com",
    description="Advanced 3D visualizer for researchers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/hh505030475/hmp-2g/tree/upload-pip/",
    project_urls={
        "Bug Tracker": "https://gitee.com/hh505030475/hmp-2g/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(where="src"),
    package_dir={'': 'src'},  # Optional
    package_data={  # Optional
        "VISUALIZE": package_files("src/VISUALIZE"),
        "UTILS": package_files("src/UTILS"),
    },
    python_requires=">=3.6",
    install_requires=_process_requirements(),
)

from setuptools import setup, find_packages
setup(
    name             = 'python-mecab-ner',
    version          = '0.0.1',
    description      = 'Test package for distribution',
    author           = 'Youngchan',
    author_email     = 'youngchanchatbot@gmail.com',
    url              = '',
    download_url     = '',
    install_requires = ['pybind11 ~= 2.0', "python-mecab-ko ~= 1.0.12"],
	include_package_data=True,
	packages=find_packages(),
    keywords         = ['Text Processing', 'Text Processing :: Linguistic', 'NER'],
    python_requires  = '>=3.7',
    zip_safe=False,
    classifiers      = [
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3 :: Only',
        "License :: OSI Approved :: MIT License",
        'Intended Audience :: Science/Research',
        'Natural Language :: Korean',
        "Operating System :: OS Independent",
    ]
)


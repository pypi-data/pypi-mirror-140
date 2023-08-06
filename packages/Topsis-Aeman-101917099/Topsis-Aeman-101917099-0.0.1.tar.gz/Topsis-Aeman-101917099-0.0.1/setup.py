import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name = 'Topsis-Aeman-101917099',         
    version = '0.0.1',      
    author = 'Aeman Singla', 
    author_email = 'aemansingla09@gmail.com',     
    license='MIT',        
    description = 'Calculate the topsis score for different models',      
    keywords = ['Topsis','Aeman Singla'],  
    install_requires=[           
            'pandas',
        ],
        classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)

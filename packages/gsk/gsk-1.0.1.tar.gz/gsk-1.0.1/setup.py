import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='gsk',  
     version='1.0.1',
     scripts=['gsk_script'] ,
     author="Shravan Kumar Gautam",
     author_email="shravan.gautam@gmail.com",
     description="A Library set of rapid application development",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="",
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     packages=[
	"gsk",
     ],
     license="MIT",
     include_package_data=True,
     install_requires=[
	"Jinja2",
	"cx_Oracle",
	"simplejson",
	"pymysql",
	"websockets",
	"websocket",
	"pyperclip",
	"flufl.bounce",
	"lambda",
	"requests",
	"python-magic"
     ]
 )

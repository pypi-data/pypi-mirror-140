<h1>Toolbox Converter for ArcGIS</h1>
<p>Version 1.0.0</p>
<p>
This small python program was made for easier use of Python Toolboxes (.pyt) in IDEs like PyCharm, Visual Studio Code, Atom and so on. The advantage is that you can write the Toolbox in pure python and the program can convert the python-script to a real Python Tool afterwards (for use in for instance ArcGIS Pro or ArcMap).
</p>
<p>
Since most IDEs don't have built in understanding of pyt-files it's a nice advantage to get the IDEs to interpret the Toolbox as a general Python-script first and then just convert it to a finished ArcGIS Tool when you want to test it in the ArcGIS Environment.
</p>
<h2>Requirements</h2>
<p>This package requires a minimum version of Python 3.5 due to the use of common 3.5 functionalities like PathLib and F-strings. This was also made with purpose of functioning alongside the ArcGIS Pro Arcpy Library which runs on Python 3.6</p>
<p>Even though this uses Python 3.5 or above to function, the final Toolboxes can still be used in earlier Python versions, given that you haven't added code in the toolboxes that are not compatible with the given Python version.</p>
<h2>Use</h2>
Install through normal pip-install or just clone this project. For pip-installation use:

```console
pip install toolbox-maker
```

The program contains two main functions. The first is a function that creates the inital python toolbox-script and puts it in a .py-file. The name of the file and toolbox is up to you just specify the name as following:

```python
import toolbox_maker as tm

tm.make_python_file(name="your_chosen_name_here")
```
In case you want to control the folder it should be placed in you can specify the folder as the first parameter:
```python
import toolbox_maker as tm

tm.make_python_file(name="your_chosen_name_here", path="your_path_here")
```

<p>
The second function is the converter itself. The only parameter it needs is what file is to be converted to a Toolbox-script. You must specify the full path here as well, although if you haven't specified a folder in the first function. The script will just use your python project folder and make its own folder there and use it for the conversion.
</p>

```python
import toolbox_maker as tm

tm.convert_to_toolbox(file_name="file_name_and_path_here")
```

<p>
In case you want to specify your own paths you can do so by following the example below:
</p>

```python
import toolbox_maker as tm

tm.convert_to_toolbox(file_name="file_name_and_path_here", 
                      file_path="path_to_your_python_file", 
                      dest_path="destination_path_for_the_toolbox")
```

<h2>Tips & Tricks</h2>
<p>
If the folder you specify in the toolbox converter does not exist, the script will create the folder in the given destination. So if you feel lazy and don't want to prepare a folder before using the script it's perfectly fine, the script will handle it for you.
</p>
<p>
Dot-descriptions are legal folder references. I.e. ./TEST/ reference a folder named "TEST" from the folder you are in, and ../ reference a folder above the folder you are in according to the folder hierarchy. These references are made legal for easier use of the folder definitions, since absolute paths are fiddly to deal with sometimes.
</p>
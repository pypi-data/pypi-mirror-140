<h1>Toolbox Converter for ArcGIS</h1>
<p>Version 0.0.1</p>
<p>
This small python program was made for easier use of Python Toolboxes (.pyt) in IDEs like PyCharm, Visual Studio Code, Atom and so on. The advantage is that you can write the Toolbox in pure python and the program can convert the python-script to a real Python Tool afterwards (for use in for instance ArcGIS Pro or ArcMap).
</p>
<p>
Since most IDEs don't have built in understanding of pyt-files it's a nice advantage to get the IDEs to interpret the Toolbox as a general Python-script first and then just convert it to a finished ArcGIS Tool when you want to test it in the ArcGIS Environment.
</p>
<h2>Use</h2>
Install through normal pip-install or just clone this project. For pip-installation use:

```console
pip install toolbox_maker
```

The program contains two main functions. The first is a function that creates the inital python toolbox-script and puts it in a .py-file. The name of the file and toolbox is up to you just specify the name as following:

```python
import toolbox_maker as tm

tm.make_python_file(name="your_chosen_name_here")
```
In case you want to control the folder it should be placed in you can specify the folder as the first parameter:
```python
import toolbox_maker as tm

tm.make_python_file(path="your_path_here", name="your_chosen_name_here")
```
Remember to use the whole path, i.e.: C:\users\xyz\Documents\ArcGISProjects
<p>
The second function is the converter itself. The only parameter it needs is what file is to be converted to a Toolbox-script. You must specify the full path here as well, although if you haven't specified a folder in the first function. The script will just use your python project folder and make its own folder there and use it for the conversion.
</p>

```python
import toolbox_maker as tm

tm.convert_to_toolbox(file_name="file_name_and_path_here")
```
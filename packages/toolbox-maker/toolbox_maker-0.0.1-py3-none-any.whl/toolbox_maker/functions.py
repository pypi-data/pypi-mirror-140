import os
import shutil
from pathlib import Path


def make_python_file(name="", path="./python_tool_code/"):
    if name != "" and ".py" in name:
        file_name = name
    elif name != "" and ".py" not in name:
        file_name = f"{name}.py"
    else:
        file_name = "tool_in_progress.py"

    tool_name = file_name.split(".")[0]

    initial_python_code = '# -*- coding: utf-8 -*-\n\n' \
                          'import arcpy\n\n\n' \
                          'class Toolbox(object):\n' \
                          '    def __init__(self):\n' \
                          '        """Define the toolbox (the name of the toolbox is the name of the.pyt file)."""\n' \
                          f'        self.label = "{ tool_name }"\n' \
                          f'        self.alias = "{ tool_name }"\n' \
                          '        # List of tool classes associated with this toolbox\n' \
                          '        self.tools = [Tool]\n\n\n' \
                          'class Tool(object):\n' \
                          '    def __init__(self):\n' \
                          '        """Define the tool (tool name is the name of the class)."""\n' \
                          '        self.label = "Tool"\n' \
                          '        self.description = ""\n' \
                          '        self.canRunInBackground = False\n\n' \
                          '    @staticmethod\n' \
                          '    def getParameterInfo():\n' \
                          '        """Define parameter definitions"""\n' \
                          '        params = None\n' \
                          '        return params\n\n' \
                          '    @staticmethod\n' \
                          '    def isLicensed():\n' \
                          '        """Set whether tool is licensed to execute."""\n' \
                          '        return True\n\n' \
                          '    def updateParameters(self, parameters):\n' \
                          '        """Modify the values and properties of parameters before internalvalidationis ' \
                          'performed.\n        This method is called whenever a parameterhas been changed."""\n' \
                          '        return\n\n' \
                          '    def updateMessages(self, parameters):\n' \
                          '        """Modify the messages created by internal validation for each toolparameter.\n' \
                          '        This method is called after internal validation."""\n' \
                          '        return\n\n' \
                          '    def execute(self, parameters, messages):\n' \
                          '        """The source code of the tool."""\n' \
                          '        return\n'

    Path(path).mkdir(parents=True, exist_ok=True)

    with open(path + file_name, "w") as python_file:
        python_file.write(initial_python_code)


def convert_to_toolbox(file_name: str, file_path="", dest_path=""):
    if file_path == "":
        original_folder = "./python_tool_code/"
    else:
        original_folder = file_path

    if dest_path == "":
        convert_folder = "./converted_toolboxes/"
    else:
        convert_folder = dest_path

    if ".py" not in file_name:
        file_name = f"{file_name}.py"

    if not os.path.exists(convert_folder):
        Path(convert_folder).mkdir(parents=True, exist_ok=True)

    orginal_full_path = original_folder + file_name
    convert_full_path = convert_folder + file_name

    try:
        shutil.copy(src=orginal_full_path, dst=convert_full_path)

        if os.path.exists(convert_full_path + "t"):
            os.remove(convert_full_path + "t")

        file = Path(convert_full_path)
        file.rename(file.with_suffix('.pyt'))

        if os.path.exists(convert_full_path):
            # Removing old files that have been copied but have not been converted to pyt-files
            os.remove(convert_full_path)
    except FileNotFoundError as fnfe:
        print("The file you specified could not be found. Please check if the file exists in the correct folder.\n" +
              str(fnfe))

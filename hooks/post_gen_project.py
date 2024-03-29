"""
Post Cookie Generation script(s)
These scripts are executed from the output folder.
If any error is raised, the cookie cutter creation fails and crashes
"""

import os
import shutil
import subprocess as sp

from pathlib import Path



def decode_string(string):
    """Helper function to covert byte-string to string, but allows normal strings"""
    try:
        return string.decode()
    except AttributeError:
        return string


def invoke_shell(command):
    try:
        output = sp.check_output(command, shell=True, stderr=sp.STDOUT)
    except sp.CalledProcessError as e:
        # Trap and print the output in a helpful way
        print(decode_string(e.output), decode_string(e.returncode))
        print(e.output)
        raise e
    print(decode_string(output))


def git_init_and_tag():
    """Invoke the initial git and tag with 0.0.0 to make an initial version for Versioneer to ID"""

    # Initialize git
    invoke_shell("git init")
    # Add files
    invoke_shell("git add .")
    invoke_shell(
        "git commit -m \"Initial commit after MDI Cookiecutter creation, version {}\"".format(
            '{{ cookiecutter._mdi_driver_cc_version }}'))
    
    if "{{ cookiecutter.language }}" == "C++":
        # Add MDI as a subtree
        invoke_shell("git subtree add --prefix={{ cookiecutter.repo_name }}/mdi https://github.com/MolSSI/MDI_Library master --squash")
    
    # Set the 0.0.0 tag
    invoke_shell("git tag 0.0.0")

def move_project_files():
    language = "{{ cookiecutter.language }}"
    project_path = Path("{{ cookiecutter.repo_name }}")
    templates_path = Path("templates")

    if language == "C++":
        source_path = templates_path / "cpp"
        mdimechanic_file = templates_path / "mdimechanic_cpp.yml"
    elif language == "Python":
        source_path = templates_path / "python"
        mdimechanic_file = templates_path / "mdimechanic_python.yml"
    else:
        raise ValueError(f"Language {language} not recognized. Please choose C++ or Python.")

    # Move language-specific files
    for item in source_path.glob("*"):
        shutil.move(str(item), project_path)

    # Move mdimechanic file if required
    if "{{ cookiecutter.use_mdimechanic }}" == "True":
        shutil.move(str(mdimechanic_file), "mdimechanic.yml")

    # Clean up templates directory
    shutil.rmtree(templates_path) 

move_project_files()
git_init_and_tag()

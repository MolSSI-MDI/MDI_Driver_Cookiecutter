"""
Post Cookie Generation script(s)
These scripts are executed from the output folder.
If any error is raised, the cookie cutter creation fails and crashes
"""

import os
import subprocess as sp



cpp_driver = """#include <iostream>
#include <mpi.h>
#include <stdexcept>
#include <string.h>
#include "mdi.h"

using namespace std;

int main(int argc, char **argv) {

  // Initialize the MPI environment
  MPI_Comm world_comm;
  MPI_Init(&argc, &argv);

  // Read through all the command line options
  int iarg = 1;
  bool initialized_mdi = false;
  while ( iarg < argc ) {

    if ( strcmp(argv[iarg],"-mdi") == 0 ) {

      // Ensure that the argument to the -mdi option was provided
      if ( argc-iarg < 2 ) {
        throw runtime_error("The -mdi argument was not provided.");
      }

      // Initialize the MDI Library
      world_comm = MPI_COMM_WORLD;
      int ret = MDI_Init(argv[iarg+1], &world_comm);
      if ( ret != 0 ) {
        throw runtime_error("The MDI library was not initialized correctly.");
      }
      initialized_mdi = true;
      iarg += 2;

    }
    else {
      throw runtime_error("Unrecognized option.");
    }

  }
  if ( not initialized_mdi ) {
    throw runtime_error("The -mdi command line option was not provided.");
  }

  // Connect to the engines
  // <YOUR CODE GOES HERE>

  // Perform the simulation
  // <YOUR CODE GOES HERE>

  // Send the "EXIT" command to each of the engines
  // <YOUR CODE GOES HERE>

  // Synchronize all MPI ranks
  MPI_Barrier(world_comm);

  return 0;
}
"""


py_driver = """
import sys

# Import the MDI Library
try:
    import mdi.MDI_Library as mdi
except:
    raise Exception("Unable to import the MDI Library")

# Import MPI Library
try:
    from mpi4py import MPI
    use_mpi4py = True
    mpi_comm_world = MPI.COMM_WORLD
except ImportError:
    use_mpi4py = False
    mpi_comm_world = None


if __name__ == "__main__":

    # Read the command-line options
    iarg = 1
    mdi_options = None
    while iarg < len(sys.argv):
        arg = sys.argv[iarg]

        if arg == "-mdi":
            mdi_options = sys.argv[iarg + 1]
            iarg += 1
        else:
            raise Exception("Unrecognized command-line option")

        iarg += 1

    # Confirm that the MDI options were provided
    if mdi_options is None:
        raise Exception("-mdi command-line option was not provided")

    # Initialize the MDI Library
    mdi.MDI_Init(mdi_options, mpi_comm_world)

    # Connect to the engines

    # Perform the simulation

    # Send the "EXIT" command to each of the engines
"""





cpp_cmake = """# Compile MDI
add_subdirectory(mdi)



# Locate MPI

find_package(MPI)
if(MPI_FOUND)
   include_directories(${MPI_INCLUDE_PATH})
else()
   configure_file(${CMAKE_CURRENT_SOURCE_DIR}/STUBS_MPI/mpi.h ${CMAKE_CURRENT_BINARY_DIR}/STUBS_MPI/mpi.h COPYONLY)
endif()



# Link to MDI

#set( MDI_LOCATION ${CMAKE_BINARY_DIR}/lib/mdi/MDI_Library/ )
set( MDI_LOCATION ${CMAKE_CURRENT_BINARY_DIR}/mdi/MDI_Library/ )
link_directories( ${MDI_LOCATION} )
include_directories(${MDI_LOCATION})



# Compile the driver

add_executable({{ cookiecutter.repo_name }}
               {{ cookiecutter.repo_name }}.cpp)
target_link_libraries({{ cookiecutter.repo_name }} mdi
                      ${MPI_LIBRARIES})



# Ensure that MPI is properly linked

if(NOT MPI_FOUND)
   target_include_directories({{ cookiecutter.repo_name }} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/STUBS_MPI/)
endif()
if(MPI_COMPILE_FLAGS)
   set_target_properties({{ cookiecutter.repo_name }} PROPERTIES
      COMPILE_FLAGS "${MPI_COMPILE_FLAGS}")
endif()
if(MPI_LINK_FLAGS)
   set_target_properties({{ cookiecutter.repo_name }} PROPERTIES
      LINK_FLAGS "${MPI_LINK_FLAGS}")
endif()
"""



py_cmake = """# Compile MDI
add_subdirectory(mdi)

# Add an __init__.py to the MDI directory, so that it can be used as a package
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/mdi/__init__.py "")

# Copy the driver file into the compile directory
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/{{ cookiecutter.repo_name }}.py ${CMAKE_CURRENT_BINARY_DIR}/{{ cookiecutter.repo_name }}.py COPYONLY)
"""



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



def write_driver_file():
    # Write a langauge-specific driver file
    if "{{ cookiecutter.language }}" == "C++":
        with open("{{ cookiecutter.repo_name }}/{{ cookiecutter.repo_name }}.cpp","w") as f:
            f.write(cpp_driver)
    elif "{{ cookiecutter.language }}" =="Python":
        with open("{{ cookiecutter.repo_name }}/{{ cookiecutter.repo_name }}.py","w") as f:
            f.write(py_driver)
    else:
        raise Exception("Unsupported language")



def write_cmake_file():
    with open("{{ cookiecutter.repo_name }}/CMakeLists.txt","w") as f:
    
        # Write a langauge-specific CMakeLists.txt file
        if "{{ cookiecutter.language }}" == "C++":
            f.write(cpp_cmake)
        elif "{{ cookiecutter.language }}" =="Python":
            f.write(py_cmake)
        else:
            raise Exception("Unsupported language")



def git_init_and_tag():
    """Invoke the initial git and tag with 0.0.0 to make an initial version for Versioneer to ID"""

    # Write the language-specific files
    write_driver_file()
    write_cmake_file()

    # Initialize git
    invoke_shell("git init")
    # Add files
    invoke_shell("git add .")
    invoke_shell(
        "git commit -m \"Initial commit after CMS Cookiecutter creation, version {}\"".format(
            '{{ cookiecutter._mdi_driver_cc_version }}'))
    # Add MDI as a subtree
    invoke_shell("git subtree add --prefix={{ cookiecutter.repo_name }}/mdi https://github.com/MolSSI/MDI_Library master --squash")
    # Set the 0.0.0 tag
    invoke_shell("git tag 0.0.0")


git_init_and_tag()

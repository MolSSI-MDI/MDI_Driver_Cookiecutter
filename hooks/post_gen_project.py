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
 
  // Initialize MDI
  if ( MDI_Init(&argc, &argv) ) {
    throw std::runtime_error("The MDI library was not initialized correctly.");
  }
 
  // Confirm that MDI was initialized successfully
  int initialized_mdi;
  if ( MDI_Initialized(&initialized_mdi) ) {
    throw std::runtime_error("MDI_Initialized failed.");
  }
  if ( ! initialized_mdi ) {
    throw std::runtime_error("MDI not initialized: did you provide the -mdi option?.");
  }
 
  // Get the correct MPI intra-communicator for this code
  if ( MDI_MPI_get_world_comm(&world_comm) ) {
    throw std::runtime_error("MDI_MPI_get_world_comm failed.");
  }
 
  // Connect to the engines
  // <YOUR CODE GOES HERE>
 
  // Perform the simulation
  // <YOUR CODE GOES HERE>
 
  // Send the "EXIT" command to each of the engines
  // <YOUR CODE GOES HERE>
 
  // Finalize MPI
  MPI_Barrier(world_comm);
  MPI_Finalize();
 
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
    mdi.MDI_Init(mdi_options)

    # Get the correct MPI intra-communicator for this code
    mpi_comm_world = mdi.MDI_MPI_get_world_comm()

    # Connect to the engines

    # Perform the simulation

    # Send the "EXIT" command to each of the engines
"""





cpp_cmake = """# Compile MDI
add_subdirectory(mdi)


# Macro to convert strings to lists

macro(string_to_list _VAR _STR)
    STRING(REPLACE "  " " " ${_VAR} "${_STR}")
    STRING(REPLACE " " ";" ${_VAR} "${_STR}")
endmacro(string_to_list _VAR _STR)


# Check for MPI

if ( NOT ( mpi STREQUAL "OFF") )
   find_package(MPI)
endif()
if( NOT MPI_FOUND )
   if( mpi STREQUAL "ON" )
      message( WARNING "Could not find MPI.  Compiling without MPI support." )
   endif()
   set(mpi "OFF")
endif()


# Add MPI stubs, if needed

if( mpi STREQUAL "OFF" )
   list(APPEND sources "${CMAKE_CURRENT_SOURCE_DIR}/STUBS_MPI/mpi.h")
endif()


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



# Add the driver as a compile target

add_executable({{ cookiecutter.repo_name }}
               {{ cookiecutter.repo_name }}.cpp)



@ Link to the MDI Library

target_link_libraries({{ cookiecutter.repo_name }} mdi)


# Include and link to MPI

if( mpi STREQUAL "ON" )

   #include MPI
   string_to_list(MPI_C_COMPILE_OPTIONS   "${MPI_C_COMPILE_FLAGS}")
   string_to_list(MPI_C_LINK_OPTIONS      "${MPI_C_LINK_FLAGS}")

   target_include_directories({{ cookiecutter.repo_name }} PRIVATE ${MPI_C_INCLUDE_PATH})
   target_compile_options({{ cookiecutter.repo_name }} PRIVATE ${MPI_C_COMPILE_OPTIONS})
   target_link_libraries({{ cookiecutter.repo_name }} ${MPI_C_LIBRARIES} ${MPI_C_LINK_OPTIONS})

elseif( mpi STREQUAL "OFF" )

   message( "Compiling without MPI." )
   target_include_directories({{ cookiecutter.repo_name }} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/STUBS_MPI/)

else()

   message( FATAL_ERROR "Value of mpi not recognized. Accepted values are: ON; OFF." )

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

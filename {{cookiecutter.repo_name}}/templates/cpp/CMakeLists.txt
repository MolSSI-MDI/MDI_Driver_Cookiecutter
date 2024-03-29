# Compile MDI
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



# Link to the MDI Library

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
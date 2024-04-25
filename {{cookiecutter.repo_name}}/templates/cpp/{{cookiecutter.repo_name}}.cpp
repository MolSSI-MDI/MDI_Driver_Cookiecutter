#include <iostream>
#include <mpi.h>
#include <stdexcept>
#include <string.h>
#include <map>
#include <memory>
#include "mdi.h"

typedef std::map<std::string, MDI_Comm> EngineMap;

EngineMap connect_to_engines(int nengines) {
  
  EngineMap engines;

  for (int iengine=0; iengine < nengines; iengine++) {

    MDI_Comm comm;
    MDI_Accept_communicator(&comm);
 
    // Determine the name of this engine
    std::unique_ptr<char[]> engine_name(new char[MDI_NAME_LENGTH]);
    MDI_Send_command("<NAME", comm);
    MDI_Recv(engine_name.get(), MDI_NAME_LENGTH, MDI_CHAR, comm);
 
    std::cout << "Engine name: " << engine_name.get() << std::endl;

    engines[engine_name.get()] = comm;

  }

  return engines;

}

void initialization(int argc, char **argv, MPI_Comm &mpi_world_comm) {

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
  if ( MDI_MPI_get_world_comm(&mpi_world_comm) ) {
    throw std::runtime_error("MDI_MPI_get_world_comm failed.");
  }
}
 
int main(int argc, char **argv) {

  // Initialize MDI and the MPI environment
  MPI_Comm world_comm;
  initialization(argc, argv, world_comm);

  // Number of engines
  int nengines = {{cookiecutter.number_of_engines}};
 
  // Connect to the engines
  EngineMap engines = connect_to_engines(nengines);
 
  /////////////////////////////////////////////////
  // Perform the simulation
  /////////////////////////////////////////////////
  
  // <YOUR CODE GOES HERE>
 
  // Send the "EXIT" command to each of the engines
  for (const auto& pair : engines) {
    MDI_Send_command("EXIT", pair.second);

    std::cout << "Disconnected from "<< pair.first << std::endl;
  }
 
  // Finalize MPI
  MPI_Barrier(world_comm);
  MPI_Finalize();
 
  return 0;
}
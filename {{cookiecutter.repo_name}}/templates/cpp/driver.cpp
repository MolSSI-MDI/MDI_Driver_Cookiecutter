#include <iostream>
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
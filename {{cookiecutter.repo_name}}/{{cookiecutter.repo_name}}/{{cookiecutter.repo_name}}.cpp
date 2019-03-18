#include <iostream>
#include <mpi.h>
#include <string.h>
extern "C" {
#include "mdi.h"
}

using namespace std;

int main(int argc, char **argv) {

  // Initialize the MPI environment
  MPI_Comm world_comm;
  MPI_Init(&argc, &argv);

  // Ensure the mdi argument has been provided 
  // NOTE: Assumes that -mdi is the first option provided
  int iarg = 1;
  if ( !( argc-iarg >= 2 && strcmp(argv[iarg],"-mdi") == 0) ) {
    throw string("The -mdi argument was not provided.");
  }

  // Initialize the MDI library
  world_comm = MPI_COMM_WORLD;
  int ret = MDI_Init(argv[iarg+1], &world_comm);
  if ( ret != 0 ) {
    throw string("The MDI library was not initialized correctly.");
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

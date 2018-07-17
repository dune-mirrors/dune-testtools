/* Tutorial quick start guide
 * \brief A program that refines a grid and outputs a vtk
 */

#include "config.h"

#include <sstream>
#include <string>
#include <dune/common/parallel/mpihelper.hh>
#include <dune/common/exceptions.hh>
#include <dune/common/parametertree.hh>
#include <dune/common/parametertreeparser.hh>
#include <dune/grid/utility/structuredgridfactory.hh>
#include <dune/grid/io/file/vtk.hh>
#include <dune/grid/yaspgrid.hh>
#include <dune/grid/uggrid.hh>

int main(int argc, char** argv) try
{
  // maybe initialize mpi
  Dune::MPIHelper::instance(argc, argv);

  // check if a single argument was supplied
  if (argc != 2)
    DUNE_THROW(Dune::InvalidStateException, "Please supply an ini file. Usage: ./" << argv[0] << " <inifile>");

  // load the parameter file
  Dune::ParameterTree params;
  Dune::ParameterTreeParser::readINITree(argv[1], params);

  // the grid type
  typedef GRIDTYPE Grid;

  // build a simple structured 2x2 unit square grid
  Dune::StructuredGridFactory<Grid> factory;
  auto grid = factory.createCubeGrid({0, 0}, {1, 1}, {{2, 2}});

  // refine the grid
  auto level = params.get<int>("level", 0);
  grid->globalRefine(level);

  // output the grid to vtk
  // note: a unique vtk filename can easily be generated in the meta ini file
  Dune::VTKWriter<typename Grid::LeafGridView> vtkwriter(grid->leafGridView());
  std::stringstream outputName;
  outputName << argv[0] << "_" << params.get<std::string>("level");
  vtkwriter.write(outputName.str());

  return 0;
}
// Error handler /////////////////
catch (Dune::Exception& e) {
    std::cerr << e << std::endl;
    return 1;
}

#ifndef DUNE_TESTTOOLS_GRIDCONSTRUCTION_HH
#define DUNE_TESTTOOLS_GRIDCONSTRUCTION_HH

#include<array>
#include<bitset>
#include<memory>
#include<sstream>

#include<dune/common/exceptions.hh>
#include<dune/common/parametertree.hh>
#include<dune/common/parallel/communication.hh>
#include<dune/grid/common/backuprestore.hh>
#include<dune/grid/io/file/dgfparser/dgfparser.hh>
#include<dune/grid/io/file/gmshreader.hh>
#include<dune/grid/utility/structuredgridfactory.hh>

// YaspGrid specific includes
#include<dune/grid/yaspgrid.hh>
#include<dune/grid/yaspgrid/backuprestore.hh>
#include<dune/grid/io/file/dgfparser/dgfyasp.hh>

// OneDGrid specific includes
#include<dune/grid/onedgrid.hh>
#include<dune/grid/io/file/dgfparser/dgfoned.hh>

// UGGrid specific includes
#if HAVE_UG
#include<dune/grid/uggrid.hh>
#include<dune/grid/io/file/dgfparser/dgfug.hh>
#endif

// ALUGrid specific includes
#if HAVE_DUNE_ALUGRID
#include<dune/alugrid/grid.hh>
#include<dune/alugrid/dgf.hh>
#endif

/**
 * \file A factory class combining all methods of grid construction under
 *       the umbrella of ini file construction.
 *
 *  There are many ways to construct dune-grids. In automated testing we want
 *  to control those ways through one mechanism - ini files. All grids only
 *  take into account key/value pairs within their group. See the factory specialization
 *  documentation to see how grids of that types can be customized through
 *  the ini files.
 *
 *  - The include list of this file could cause dependency trouble. So it either
 *    needs to know through the preprocessor, which grids are actually used or
 *    the specialization need to be split into grid specific headers and be
 *    included in the main program iff the grid is used.
 */

/** Default Implementation of factory class constructing grids from ini
 *
 *  throws an exception upon construction.
 */
template<class GRID>
class IniGridFactory
{
  typedef GRID Grid;
  IniGridFactory(const Dune::ParameterTree& params, std::string section = "default")
  {
    DUNE_THROW(Dune::NotImplemented,
        "The specialization of the IniGridFactory for your Grid is not implemented!");
  }
};

/** An IniGridFactory for equidistant YaspGrid
 *
 * The following keys are recognized:
 * - loadFromFile : a filename to restore the grid from
 * - dgfFile : a dgf file to load the coarse grid from
 * - extension : extension of the domain
 * - cells : the number of cells in each direction
 * - periodic : true or false for each direction
 * - overlap : overlap size in cells
 * - partitioning : a non standard load-balancing, number of processors per direction
 * - keepPyhsicalOverlap : whether to keep the physical overlap
 *     in physical size or in number of cells upon refinement
 * - refinement : the number of global refines to apply initially.
 */
template<class ct, int dim>
class IniGridFactory<Dune::YaspGrid<dim, Dune::EquidistantCoordinates<ct, dim> > >
{
public:
  typedef typename Dune::YaspGrid<dim, Dune::EquidistantCoordinates<ct, dim> > Grid;

  IniGridFactory(const Dune::ParameterTree& params)
  {
    // When restoring, no further work is necessary
    if (params.hasKey("loadFromFile")) {
      grid = std::shared_ptr < Grid
          > (Dune::BackupRestoreFacility<Grid>::restore(
              params.get<std::string>("loadFromFile")));
      return;
    }

    if (params.hasKey("dgfFile"))
    {
      std::string dgffile = params.get<std::string>("dgfFile");
      Dune::GridPtr<Grid> gridptr(dgffile);
      grid = std::shared_ptr<Grid>(gridptr.release());

    } else {

      // extract all constructor parameters from the ini file
      // upper right corner
      Dune::FieldVector<ct, dim> extension = params.get<
          Dune::FieldVector<ct, dim> >("extension");

      // number of cells per direction
      std::array<int, dim> cells = params.get<std::array<int, dim> >(
          "cells");

      // periodicity
      std::bitset<dim> periodic;
      periodic = params.get<std::bitset<dim> >("periodic", periodic);

      // overlap cells
      int overlap = params.get<int>("overlap", 1);

      // (eventually) a non-standard load balancing
      bool default_lb = true;
      std::array<int, dim> partitioning;
      if (params.hasKey("partitioning"))
      {
        default_lb = false;
        partitioning = params.get<std::array<int, dim> >(
            "partitioning");
      }

      // build the actual grid
      if (default_lb)
        grid = std::make_shared<Grid> (extension, cells, periodic, overlap);
      else
      {
        typename Dune::YaspFixedSizePartitioner<dim> lb(partitioning);
        grid = std::make_shared<Grid> (extension, cells, periodic, overlap,
            typename Grid::CollectiveCommunicationType(), &lb);
      }
    }

    // do refinement
    bool keepPhysicalOverlap = params.get<bool>(
        "keepPhysicalOverlap", true);
    grid->refineOptions(keepPhysicalOverlap);

    int refinement = params.get<int>("refinement", 0);
    grid->globalRefine(refinement);
  }

  IniGridFactory(const Dune::ParameterTree& params, std::string section)
    : IniGridFactory(params.sub(section))
  {}

  std::shared_ptr<Grid> getGrid()
  {
    return grid;
  }

private:
  std::shared_ptr<Grid> grid;
};

/** An IniGridFactory for equidistant YaspGrid with non-zero offset
 *
 * The following keys are recognized:
 * - lowerleft/origin : The coordinate of the lower left corner
 * - upperright : The coordinate of the upper right corner.
 * - extension : extension of the domain, only taken into account if no
 *     upperright key was found.
 * - cells : the number of cells in each direction
 * - periodic : true or false for each direction
 * - overlap : overlap size in cells
 * - partitioning : a non standard load-balancing, number of processors per direction
 * - keepPyhsicalOverlap : whether to keep the physical overlap
 *     in physical size or in number of cells upon refinement
 * - refinement : the number of global refines to apply initially.
 */
template<class ct, int dim>
class IniGridFactory<
    Dune::YaspGrid<dim, Dune::EquidistantOffsetCoordinates<ct, dim> > >
{
public:
  typedef typename Dune::YaspGrid<dim,
      Dune::EquidistantOffsetCoordinates<ct, dim> > Grid;

  IniGridFactory(const Dune::ParameterTree& params)
  {
    if (params.hasKey("loadFromFile")) {
      grid = std::shared_ptr < Grid
          > (Dune::BackupRestoreFacility<Grid>::restore(
              params.get<std::string>("loadFromFile")));
      return;
    }

    // extract all constructor parameters from the ini file
    // upper right corner
    Dune::FieldVector<ct, dim> lowerleft = params.get<
        Dune::FieldVector<ct, dim> >("lowerleft");

    Dune::FieldVector<ct, dim> upperright(lowerleft);
    if (params.hasKey("upperright"))
      upperright = params.get<Dune::FieldVector<ct, dim> >(
          "upperright");
    else
    {
      Dune::FieldVector<ct, dim> extension = params.get<
          Dune::FieldVector<ct, dim> >("extension");
      upperright += extension;
    }

    // number of cells per direction
    std::array<int, dim> cells = params.get<std::array<int, dim> >(
        "cells");

    // periodicity
    std::bitset<dim> periodic;
    periodic = params.get<std::bitset<dim> >("periodic", periodic);

    // overlap cells
    int overlap = params.get<int>("overlap", 1);

    // (eventually) a non-standard load balancing
    bool default_lb = true;
    std::array<int, dim> partitioning;
    if (params.hasKey("partitioning"))
    {
      default_lb = false;
      partitioning = params.get<std::array<int, dim> >(
          "partitioning");
    }

    // build the actual grid
    if (default_lb)
      grid = std::make_shared < Grid
          > (lowerleft, upperright, cells, periodic, overlap);
    else
    {
      typename Dune::YaspFixedSizePartitioner<dim> lb(partitioning);
      grid =
          std::make_shared < Grid
              > (lowerleft, upperright, cells, periodic, overlap, typename Grid::CollectiveCommunicationType(), &lb);
    }

    bool keepPhysicalOverlap = params.get<bool>(
        "keepPhysicalOverlap", true);
    grid->refineOptions(keepPhysicalOverlap);

    int refinement = params.get<int>("refinement", 0);
    grid->globalRefine(refinement);
  }

  IniGridFactory(const Dune::ParameterTree& params, std::string section)
    : IniGridFactory(params.sub(section))
  {}

  std::shared_ptr<Grid> getGrid()
  {
    return grid;
  }

private:
  std::shared_ptr<Grid> grid;
};

/** An IniGridFactory for a tensorproduct YaspGrid
 *
 * The following keys are recognized:
 * - coordinates0..coordinates[dim-1] : the coordinate vector
 * - periodic : true or false for each direction
 * - overlap : overlap size in cells
 * - partitioning : a non standard load-balancing, number of processors per direction
 * - keepPyhsicalOverlap : whether to keep the physical overlap
 *     in physical size or in number of cells upon refinement
 * - refinement : the number of global refines to apply initially.
 */
template<class ct, int dim>
class IniGridFactory<
    Dune::YaspGrid<dim, Dune::TensorProductCoordinates<ct, dim> > >
{
public:
  typedef typename Dune::YaspGrid<dim, Dune::TensorProductCoordinates<ct, dim> > Grid;

  IniGridFactory(const Dune::ParameterTree& params)
  {
    if (params.hasKey("loadFromFile")) {
      grid = std::shared_ptr < Grid
          > (Dune::BackupRestoreFacility<Grid>::restore(
              params.get<std::string>("loadFromFile")));
      return;
    }

    std::array<std::vector<ct>, dim> coordinates;
    for (int i = 0; i < dim; ++i)
    {
      std::ostringstream key_str;
      key_str << "coordinates" << i;
      coordinates[i] = params.get<std::vector<ct> >(key_str.str());
    }

    // periodicity
    std::bitset<dim> periodic;
    periodic = params.get<std::bitset<dim> >("periodic", periodic);

    // overlap cells
    int overlap = params.get<int>("overlap", 1);

    // (eventually) a non-standard load balancing
    bool default_lb = true;
    std::array<int, dim> partitioning;
    if (params.hasKey("partitioning"))
    {
      default_lb = false;
      partitioning = params.get<std::array<int, dim> >(
          "partitioning");
    }

    // build the actual grid
    if (default_lb)
      grid = std::make_shared < Grid > (coordinates, periodic, overlap);
    else
    {
      typename Dune::YaspFixedSizePartitioner<dim> lb(partitioning);
      grid =
          std::make_shared < Grid
              > (coordinates, periodic, overlap, typename Grid::CollectiveCommunicationType(), &lb);
    }

    bool keepPhysicalOverlap = params.get<bool>(
        "keepPhysicalOverlap", true);
    grid->refineOptions(keepPhysicalOverlap);

    int refinement = params.get<int>("refinement", 0);
    grid->globalRefine(refinement);
  }

  IniGridFactory(const Dune::ParameterTree& params, std::string section)
    : IniGridFactory(params.sub(section))
  {}

  std::shared_ptr<Grid> getGrid()
  {
    return grid;
  }

private:
  std::shared_ptr<Grid> grid;
};


/** An IniGridFactory for a OneDGrid
 *
 * The following keys are recognized:
 * - dgfFile : a dgf file to load the coarse grid from
 * - coords : A coordinate list (of course forming a monotonous sequence)
 * - left : coordinate of the left interval boundary
 * - right : coordinate of the right interval boundary
 * - cells : the number of cells in each direction
 * - refinement : the number of global refines to apply initially.
 */
template<>
class IniGridFactory<Dune::OneDGrid>
{
public:
  typedef typename Dune::OneDGrid Grid;
  typedef typename Grid::ctype ct;

  IniGridFactory(const Dune::ParameterTree& params)
  {
    if (params.hasKey("dgfFile"))
    {
      std::string dgffile = params.get<std::string>("dgfFile");
      Dune::GridPtr<Grid> gridptr(dgffile);
      grid = std::shared_ptr<Grid>(gridptr.release());
    }
    else if (params.hasKey("coords"))
    {
      auto coords = params.get<std::vector<ct>>("coords");
      grid = std::make_shared<Grid>(coords);
    }
    else
    {
      // extract the interval extensions from the ini file
      ct left = params.get<ct>("left");
      ct right = params.get<ct>("right");

      // number of cells per direction
      int cells = params.get<int>("cells");

      grid = std::make_shared<Grid>(cells, left, right);
    }

    int refinement = params.get<int>("refinement", 0);
    grid->globalRefine(refinement);
  }

  IniGridFactory(const Dune::ParameterTree& params, std::string section)
    : IniGridFactory(params.sub(section))
  {}

  std::shared_ptr<Grid> getGrid()
  {
    return grid;
  }

private:
  std::shared_ptr<Grid> grid;
};


#if HAVE_UG
/** An IniGridFactory for an UGGrid
 *
 * The grid is constructed through different mechanism with
 * the following priority order:
 * 1) GMSH import
 * 2) DGF import
 * 3) construct a structured grid from the given parameters
 *
 * The following keys are recognized:
 * - gmshFile : A gmsh file to load from
 * - dgfFile : a DGF file to load from
 * - lowerleft : lowerleft corner of a structured grid
 * - upperright : upperright corner of a structured grid
 * - elements : number of elements in a structured grid
 * - elementType : "quadrilateral" or "simplicial" to be used for structured grids
 * - refinement : the number of global refines to perform
 * - verbose : whether the grid construction should output to standard out
 * - boundarySegments : whether to insert boundary segments into the grid
 */
template<int dim>
class IniGridFactory<Dune::UGGrid<dim> >
{
public:
  typedef typename Dune::UGGrid<dim> Grid;
  typedef typename Grid::ctype ct;

  IniGridFactory(const Dune::ParameterTree& params)
  {
    // try building an ug grid by taking a gmshfile from the ini file

    if (params.hasKey("gmshFile"))
    {
      std::string gmshfile = params.get<std::string>("gmshFile");

      bool verbose = params.get<bool>("verbose", false);
      bool boundarySegments = params.get<bool>("boundarySegments", false);

      grid =
          std::shared_ptr < Grid
              > (Dune::GmshReader<Grid>::read(gmshfile, verbose,
                  boundarySegments));
    }
    else if (params.hasKey("dgfFile"))
    {
      std::string dgffile = params.get<std::string>("dgfFile");
      Dune::GridPtr<Grid> gridptr(dgffile);
      grid = std::shared_ptr < Grid > (gridptr.release());
    } else {
      Dune::FieldVector<ct, dim> lowerleft = params.get<
          Dune::FieldVector<ct, dim> >("lowerleft",
          Dune::FieldVector<ct, dim>(0.0));
      Dune::FieldVector<ct, dim> upperright = params.get<
          Dune::FieldVector<ct, dim> >("upperright");

      std::array<unsigned int, dim> elements;
      std::fill(elements.begin(), elements.end(), 1);
      if (params.hasKey("elements"))
        elements = params.get<std::array<unsigned int, dim> >("elements");

      std::string elemType = params.get<std::string>("elementType",
          "quadrilateral");

      Dune::StructuredGridFactory<Grid> factory;
      // TODO maybe add some synonymous descriptions of quadrilateral grids here.
      if (elemType == "quadrilateral")
        grid = factory.createCubeGrid(lowerleft, upperright, elements);
      else if (elemType == "simplicial")
        grid = factory.createSimplexGrid(lowerleft, upperright, elements);
      else
        DUNE_THROW(Dune::GridError,
            "Specified an invalid element type in ini file.");
    }

    // given we have successfully created a grid, maybe perform some operations on it
    // TODO what are suitable such operations for an unstructured grid.
    grid->loadBalance();
    int refinement = params.get<int>("refinement", 0);
    grid->globalRefine(refinement);
  }

  IniGridFactory(const Dune::ParameterTree& params, std::string section)
    : IniGridFactory(params.sub(section))
  {}

  std::shared_ptr<Grid> getGrid()
  {
    return grid;
  }

private:
  std::shared_ptr<Grid> grid;
};

#endif // HAVE_UG

#if HAVE_DUNE_ALUGRID
/** An IniGridFactory for an ALUGrid
 *
 * All keys are expected to be in group alu.
 *
 * The grid is constructed through different mechanism with
 * the following priority order:
 * 1) GMSH import
 * 2) DGF import
 * 2) construct a structured grid from the given parameters
 *
 * The following keys are recognized:
 * - gmshFile : A gmsh file to load from
 * - dgfFile : a DGF file to load from
 * - lowerleft : lowerleft corner of a structured grid
 * - upperright : upperright corner of a structured grid
 * - elements : number of elements in a structured grid
 * - refinement : the number of global refines to perform
 * - verbose : whether the grid construction should output to standard out
 * - boundarySegments : whether to insert boundary segments into the grid
 */
template<int griddim, int worlddim, Dune::ALUGridElementType elType, Dune::ALUGridRefinementType refinementType>
class IniGridFactory<Dune::ALUGrid<griddim, worlddim, elType, refinementType> >
{
public:
  typedef typename Dune::ALUGrid<griddim, worlddim, elType, refinementType> Grid;

  IniGridFactory(const Dune::ParameterTree& params)
  {

    if (params.hasKey("gmshFile"))
    {
      std::string gmshfile = params.get<std::string>("gmshFile");

      bool verbose = params.get<bool>("verbose", false);
      bool boundarySegments = params.get<bool>("boundarySegments", false);

      grid = std::shared_ptr < Grid
              > (Dune::GmshReader<Grid>::read(gmshfile, verbose,
                  boundarySegments));
    }
    else if (params.hasKey("dgfFile"))
    {
      std::string dgffile = params.get<std::string>("dgfFile");
      Dune::GridPtr<Grid> gridptr(dgffile);
      grid = std::shared_ptr < Grid > (gridptr.release());
    } else {

      typedef Dune::FieldVector<typename Grid::ctype,worlddim> Coord;
      Coord lowerLeft = params.get<Coord>("lowerleft", Coord(0));
      Coord upperRight = params.get<Coord>("upperright", Coord(1));
      std::array<unsigned int,griddim> elements;
      std::fill(elements.begin(), elements.end(), 1);
      if (params.hasKey("elements"))
        elements = params.get<std::array<unsigned int, griddim> >("elements");

      Dune::StructuredGridFactory<Grid> factory;
      if (elType == Dune::simplex)
        grid = factory.createSimplexGrid(lowerLeft, upperRight, elements);
      else if (elType == Dune::cube)
        grid = factory.createCubeGrid(lowerLeft, upperRight, elements);
      else
        DUNE_THROW(Dune::GridError,
            "The element type specified for the grid is unknown to the IniGridFactory!");
    }
    grid->loadBalance();
    int refinement = params.get<int>("refinement", 0);
    grid->globalRefine(refinement);
  }

  IniGridFactory(const Dune::ParameterTree& params, std::string section)
    : IniGridFactory(params.sub(section))
  {}

  std::shared_ptr<Grid> getGrid()
  {
    return grid;
  }

private:
  std::shared_ptr<Grid> grid;
};

#endif //HAVE_DUNE_ALUGRID

#endif

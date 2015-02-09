#ifndef DUNE_TESTTOOLS_GRIDCONSTRUCTION_HH
#define DUNE_TESTTOOLS_GRIDCONSTRUCTION_HH

#include<array>
#include<bitset>
#include<memory>
#include<sstream>

#include<dune/common/exceptions.hh>
#include<dune/common/parametertree.hh>
#include<dune/common/parallel/collectivecommunication.hh>
#include<dune/grid/common/backuprestore.hh>
#include<dune/grid/io/file/dgfparser/dgfparser.hh>
#include<dune/grid/io/file/gmshreader.hh>
#include<dune/grid/utility/structuredgridfactory.hh>

// YaspGrid specific includes
#include<dune/grid/yaspgrid.hh>
#include<dune/grid/yaspgrid/backuprestore.hh>
#include<dune/grid/io/file/dgfparser/dgfyasp.hh>

// UGGrid specific includes
#include<dune/grid/uggrid.hh>
#include<dune/grid/io/file/dgfparser/dgfug.hh>

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
 *  TODO:
 *  - It is currently impossible to construct multiple grids of one type.
 *    This should be possible by taking a subtree to construct the grid.
 *    => The main program can control multiple groups within the ini file.
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
  IniGridFactory(const Dune::ParameterTree& params)
  {
    DUNE_THROW(Dune::NotImplemented,
        "The IniGridFactory for your Grid are not implemented!");
  }
};

/** An IniGridFactory for equidistant YaspGrid
 *
 * All keys are expected to be in group yaspgrid.
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
    try
    {
      if (params.hasKey("yaspgrid.loadFromFile"))
        grid = std::shared_ptr < Grid
            > (Dune::BackupRestoreFacility<Grid>::restore(
                params.get<std::string>("yaspgrid.loadFromFile")));
      else
        DUNE_THROW(Dune::Exception, "Execute catch in that case");
    }
    catch (...)
    {
      try
      {
        if (params.hasKey("yaspgrid.dgfFile"))
        {
          std::string dgffile = params.get<std::string>("yaspgrid.dgfFile");
          Dune::GridPtr<Grid> gridptr(dgffile);
          grid = std::shared_ptr<Grid>(gridptr.release());
        }
        else
          DUNE_THROW(Dune::Exception, "Execute catch block in that case");
      }
      catch (...)
      {
        // extract all constructor parameters from the ini file
        // upper right corner
        Dune::FieldVector<ct, dim> extension = params.get<
            Dune::FieldVector<ct, dim> >("yaspgrid.extension");

        // number of cells per direction
        std::array<int, dim> cells = params.get<std::array<int, dim> >(
            "yaspgrid.cells");

        // periodicity
        std::bitset<dim> periodic;
        periodic = params.get<std::bitset<dim> >("yaspgrid.periodic", periodic);

        // overlap cells
        int overlap = params.get<int>("yaspgrid.overlap", 1);

        // (eventually) a non-standard load balancing
        bool default_lb = true;
        std::array<int, dim> partitioning;
        if (params.hasKey("yaspgrid.partitioning"))
        {
          default_lb = false;
          partitioning = params.get<std::array<int, dim> >(
              "yaspgrid.partitioning");
        }

        // build the actual grid
        if (default_lb)
          grid = std::make_shared < Grid
              > (extension, cells, periodic, overlap);
        else
        {
          typename Dune::YaspFixedSizePartitioner<dim> lb(partitioning);
          grid =
              std::make_shared < Grid
                  > (extension, cells, periodic, overlap, typename Grid::CollectiveCommunicationType(), &lb);
        }
      }

      bool keepPhysicalOverlap = params.get<bool>(
          "yaspgrid.keepPhysicalOverlap", true);
      grid->refineOptions(keepPhysicalOverlap);

      int refinement = params.get<int>("yaspgrid.refinement", 0);
      grid->globalRefine(refinement);
    }
  }

  std::shared_ptr<Grid> getGrid()
  {
    return grid;
  }

private:
  std::shared_ptr<Grid> grid;
};

/** An IniGridFactory for equidistant YaspGrid with non-zero offset
 *
 * All keys are expected to be in group yaspgrid.
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
    try
    {
      if (params.hasKey("yaspgrid.loadFromFile"))
        grid = std::shared_ptr < Grid
            > (Dune::BackupRestoreFacility<Grid>::restore(
                params.get<std::string>("yaspgrid.loadFromFile")));
      else
        DUNE_THROW(Dune::Exception, "Execute catch in that case");
    }
    catch (...)
    {
      // extract all constructor parameters from the ini file
      // upper right corner
      Dune::FieldVector<ct, dim> lowerleft = params.get<
          Dune::FieldVector<ct, dim> >("yaspgrid.lowerleft");

      Dune::FieldVector<ct, dim> upperright(lowerleft);
      if (params.hasKey("upperright"))
        upperright = params.get<Dune::FieldVector<ct, dim> >(
            "yaspgrid.upperright");
      else
      {
        Dune::FieldVector<ct, dim> extension = params.get<
            Dune::FieldVector<ct, dim> >("yaspgrid.extension");
        upperright += extension;
      }

      // number of cells per direction
      std::array<int, dim> cells = params.get<std::array<int, dim> >(
          "yaspgrid.cells");

      // periodicity
      std::bitset<dim> periodic;
      periodic = params.get<std::bitset<dim> >("yaspgrid.periodic", periodic);

      // overlap cells
      int overlap = params.get<int>("yaspgrid.overlap", 1);

      // (eventually) a non-standard load balancing
      bool default_lb = true;
      std::array<int, dim> partitioning;
      if (params.hasKey("yaspgrid.partitioning"))
      {
        default_lb = false;
        partitioning = params.get<std::array<int, dim> >(
            "yaspgrid.partitioning");
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
          "yaspgrid.keepPhysicalOverlap", true);
      grid->refineOptions(keepPhysicalOverlap);

      int refinement = params.get<int>("yaspgrid.refinement", 0);
      grid->globalRefine(refinement);
    }
  }

  std::shared_ptr<Grid> getGrid()
  {
    return grid;
  }

private:
  std::shared_ptr<Grid> grid;
};

/** An IniGridFactory for a tensorproduct YaspGrid
 *
 * All keys are expected to be in group yaspgrid.
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
    try
    {
      if (params.hasKey("yaspgrid.loadFromFile"))
        grid = std::shared_ptr < Grid
            > (Dune::BackupRestoreFacility<Grid>::restore(
                params.get<std::string>("yaspgrid.loadFromFile")));
      else
        DUNE_THROW(Dune::Exception, "Execute catch in that case");
    }
    catch (...)
    {
      std::array<std::vector<ct>, dim> coordinates;
      for (int i = 0; i < dim; ++i)
      {
        std::ostringstream key_str;
        key_str << "yaspgrid.coordinates" << i;
        coordinates[i] = params.get<std::vector<ct> >(key_str.str());
      }

      // periodicity
      std::bitset<dim> periodic;
      periodic = params.get<std::bitset<dim> >("yaspgrid.periodic", periodic);

      // overlap cells
      int overlap = params.get<int>("yaspgrid.overlap", 1);

      // (eventually) a non-standard load balancing
      bool default_lb = true;
      std::array<int, dim> partitioning;
      if (params.hasKey("yaspgrid.partitioning"))
      {
        default_lb = false;
        partitioning = params.get<std::array<int, dim> >(
            "yaspgrid.partitioning");
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
          "yaspgrid.keepPhysicalOverlap", true);
      grid->refineOptions(keepPhysicalOverlap);

      int refinement = params.get<int>("yaspgrid.refinement", 0);
      grid->globalRefine(refinement);
    }
  }

  std::shared_ptr<Grid> getGrid()
  {
    return grid;
  }

private:
  std::shared_ptr<Grid> grid;
};

/** An IniGridFactory for an UGGrid
 *
 * All keys are expected to be in group uggrid.
 *
 * The grid is constructed through different mechanism with
 * the following priority order:
 * 1) GMSH import
 * 2) DGF import
 * 3) construct a structured grid from the given parameters
 *
 * The following keys are recognized:
 * - gmshFile : A gmsh file to load from
 * - dgfFile : A DGF File to load from
 * - lowerleft : lowerleft corner of a structured grid
 * - upperright : upperright corner of a structured grid
 * - elements : number of elements in a structured grid
 * - elementType : "quadrialteral" or "simplical" to be used for structured grids
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
    try
    {
      if (params.hasKey("ug.gmshFile"))
      {
        std::string gmshfile = params.get<std::string>("ug.gmshFile");

        bool verbose = params.get<bool>("ug.verbose", false);
        bool boundarySegments = params.get<bool>("ug.boundarySegments", false);

        grid =
            std::shared_ptr < Grid
                > (Dune::GmshReader<Grid>::read(gmshfile, verbose,
                    boundarySegments));
      }
      else
        DUNE_THROW(Dune::Exception, "Execute catch in that case");
    }
    // otherwise, try other methods
    catch (...)
    {
      // try building an ug grid by taking a dgf file from the ini file
      try
      {
        if (params.hasKey("ug.dgfFile"))
        {
          std::string dgffile = params.get<std::string>("ug.dgfFile");
          Dune::GridPtr<Grid> gridptr(dgffile);
          grid = std::shared_ptr < Grid > (gridptr.release());
        }
        else
          DUNE_THROW(Dune::Exception, "Execute catch in that case");
      }
      // otherwise, try other methods
      catch (...)
      {
        // TODO construct a structured grid with the given geometry type and extensions:

        Dune::FieldVector<ct, dim> lowerleft = params.get<
            Dune::FieldVector<ct, dim> >("ug.lowerleft",
            Dune::FieldVector<ct, dim>(0.0));
        Dune::FieldVector<ct, dim> upperright = params.get<
            Dune::FieldVector<ct, dim> >("ug.upperright");

        std::array<unsigned int, dim> elements;
        std::fill(elements.begin(), elements.end(), 1);
        if (params.hasKey("ug.elements"))
          elements = params.get<std::array<unsigned int, dim> >("ug.elements");

        std::string elemType = params.get<std::string>("ug.elementType",
            "quadrilateral");

        Dune::StructuredGridFactory<Grid> factory;
        // TODO maybe add some synonymous descriptions of quadrilateral grids here.
        if (elemType == "quadrilateral")
          grid = factory.createCubeGrid(lowerleft, upperright, elements);
        else
        {
          if (elemType == "simplical")
            grid = factory.createSimplexGrid(lowerleft, upperright, elements);
          else
            DUNE_THROW(Dune::GridError,
                "Specified an invalid element type in ini file.");
        }
      }
    }

    // given we have successfully created a grid, maybe perform some operations on it
    // TODO what are suitable such operations for an unstructured grid.
    int refinement = params.get<int>("ug.refinement", 0);
    grid->globalRefine(refinement);
  }

  std::shared_ptr<Grid> getGrid()
  {
    return grid;
  }

private:
  std::shared_ptr<Grid> grid;
};

#endif

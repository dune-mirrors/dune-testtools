#ifndef DUNE_TESTTOOLS_GRIDCONSTRUCTION_HH
#define DUNE_TESTTOOLS_GRIDCONSTRUCTION_HH

#include<array>
#include<bitset>
#include<sstream>

#include<dune/common/exceptions.hh>
#include<dune/common/parametertree.hh>
#include<dune/common/parallel/collectivecommunication.hh>
#include<dune/grid/yaspgrid.hh>
#include<dune/grid/yaspgrid/backuprestore.hh>

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
        grid = Dune::BackupRestoreFacility < Grid
            > ::restore(params.get<std::string>("yaspgrid.loadFromFile"));
      else
        DUNE_THROW(Dune::Exception, "Execute catch in that case");
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
        grid = new Grid(extension, cells, periodic, overlap);
      else
      {
        typename Dune::YLoadBalanceBackup<dim> lb(partitioning);
        grid = new Grid(extension, cells, periodic, overlap,
            typename Grid::CollectiveCommunicationType(), &lb);
      }

      bool keepPhysicalOverlap = params.get<bool>(
          "yaspgrid.keepPhysicalOverlap", true);
      grid->refineOptions(keepPhysicalOverlap);

      int refinement = params.get<int>("yaspgrid.refinement", 0);
      grid->globalRefine(refinement);
    }
  }

  ~IniGridFactory()
  {
    delete grid;
  }

  Grid& getGrid()
  {
    return *grid;
  }

private:
  Grid* grid;
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
        grid = Dune::BackupRestoreFacility < Grid
            > ::restore(params.get<std::string>("yaspgrid.loadFromFile"));
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
        grid = new Grid(lowerleft, upperright, cells, periodic, overlap);
      else
      {
        typename Dune::YLoadBalanceBackup<dim> lb(partitioning);
        grid = new Grid(lowerleft, upperright, cells, periodic, overlap,
            typename Grid::CollectiveCommunicationType(), &lb);
      }

      bool keepPhysicalOverlap = params.get<bool>(
          "yaspgrid.keepPhysicalOverlap", true);
      grid->refineOptions(keepPhysicalOverlap);

      int refinement = params.get<int>("yaspgrid.refinement", 0);
      grid->globalRefine(refinement);
    }
  }

  ~IniGridFactory()
  {
    delete grid;
  }

  Grid& getGrid()
  {
    return *grid;
  }

private:
  Grid* grid;
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
        grid = Dune::BackupRestoreFacility < Grid
            > ::restore(params.get<std::string>("yaspgrid.loadFromFile"));
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
        grid = new Grid(coordinates, periodic, overlap);
      else
      {
        typename Dune::YLoadBalanceBackup<dim> lb(partitioning);
        grid = new Grid(coordinates, periodic, overlap,
            typename Grid::CollectiveCommunicationType(), &lb);
      }

      bool keepPhysicalOverlap = params.get<bool>(
          "yaspgrid.keepPhysicalOverlap", true);
      grid->refineOptions(keepPhysicalOverlap);

      int refinement = params.get<int>("yaspgrid.refinement", 0);
      grid->globalRefine(refinement);
    }
  }

  ~IniGridFactory()
  {
    delete grid;
  }

  Grid& getGrid()
  {
    return *grid;
  }

private:
  Grid* grid;
};


#endif

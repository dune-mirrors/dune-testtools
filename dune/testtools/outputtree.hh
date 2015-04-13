#ifndef DUNE_COMMON_OUTPUTTREE_HH
#define DUNE_COMMON_OUTPUTTREE_HH

#include <fstream>
#include <string>

#include <dune/common/exceptions.hh>
#include <dune/common/parametertree.hh>
#include <dune/common/parametertreeparser.hh>

namespace Dune
{

  /** \brief a keyword list of data to collect for output
   *
   *  Log files are only to a limited extent a good way of storing
   *  program information. For automated testing, the possibility
   *  to write information in a dict-style seems important.
   *
   *  This class inherits from Dune::ParameterTree. It should implement
   *  all functionality that is desirable for the ParameterTree to be
   *  used as an output data structure. At some point, we should make
   *  a feature request for dune-common of it.
   *
   *  A list of features:
   *  * Constructor with a filename. Implicit writing to stream on destruction.
   *  * A set method that automatically converts the given value to a string through an ostringstream
   */
  class OutputTree : public ParameterTree
  {
  public:
  	/** \brief Constructor for an output tree
	   *  \param filename the filename to write
	   */
    OutputTree(const std::string& filename) : _filename(filename)
    {}

    /** \brief Constructor for an output tree
     *  \param params a Dune::ParameterTree aka the parsed ini file
     */
    OutputTree(const Dune::ParameterTree& params) : _params(params)
    {
      // if not output name is specified the ini name is the default
      if(params.hasKey("__output_name"))
        _filename = params["__output_name"];
      else
      {
        if(!params.hasKey("__name"))
          DUNE_THROW(Dune::IOError, "The meta ini syntax requires a __name key!");

        _filename = params["__name"];
      }

      // add the file extension
      _filename += ".";
      if(!params.hasKey("__output_extension"))
          DUNE_THROW(Dune::IOError, "Mandatory parameter __output_extension not set!");

      _filename += params["__output_extension"];
    }

    /** \brief Destructor for the output tree
     *  Trigger writing the collected information to a file.
     */
    ~OutputTree()
    {
      std::ofstream file;
      file.open(_filename);
      report(file);
      file.close();
    }

    template<typename T1, typename T2>
    void setConvergenceData(const T1& norm, const T2& quantity)
    {
      if(!_params.hasKey("__CONVERGENCE_TEST.NormType"))
        DUNE_THROW(Dune::IOError, "Mandatory parameter __CONVERGENCE_TEST.NormType is not set!");
      if(!_params.hasKey("__CONVERGENCE_TEST.QuantityName"))
        DUNE_THROW(Dune::IOError, "Mandatory parameter __CONVERGENCE_TEST.QuantityName is not set!");

      set<T1>(_params["__CONVERGENCE_TEST.NormType"], norm);
      set<T2>(_params["__CONVERGENCE_TEST.QuantityName"], quantity);
    }

    template<typename T>
    void set(const std::string& key, const T& arg)
    {
      std::ostringstream sstr;
      sstr << arg;
      (*this)[key] = sstr.str();
    }

  private:
    std::string _filename;
    Dune::ParameterTree _params;
  };

} // namespace Dune

#endif //DUNE_COMMON_OUTPUTTREE_HH

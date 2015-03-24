#ifndef DUNE_COMMON_OUTPUTTREE_HH
#define DUNE_COMMON_OUTPUTTREE_HH

#include<fstream>
#include<string>

#include<dune/common/parametertree.hh>

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

    template<typename T>
    void set(const std::string& key, const T& arg)
    {
      std::ostringstream sstr;
      sstr << arg;
      (*this)[key] = sstr.str();
    }

  private:
    std::string _filename;
  };

} // namespace Dune

#endif //DUNE_COMMON_OUTPUTTREE_HH

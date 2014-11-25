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
   *  This class offers a feature to have a prefix that is appended to all
   *  calls. These are managed in a stack-like fashion. Some remarks
   *  - We should think about actually implementing it with a stack
   *  - Maybe we should opt for inclusion of such feature in the parametertree itself
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

    /** \brief append a subgroup to the current prefix
     *  \param groupKey the name of the subgroup key to append to the prefix
     *
     *  The prefix will be appended to all keys given to tree operations.
     */
    void pushPrefix(const std::string& groupKey)
    {
      if (_subPrefix == "")
      	_subPrefix = groupKey;
      else
      	_subPrefix = _subPrefix + "." + groupKey;
    }

    /** \brief delete one subgroup form the current prefix
     *
     */
    void popPrefix()
    {
    	// find the index of the last occurence of the char '.'
    	std::size_t pos = 0;
    	std::size_t next = _subPrefix.find('.',0);
    	while(next != std::string::npos)
    	{
    		pos = next;
    		next = _subPrefix.find('.', pos+1);
    	}

    	// cut the appropriate prefix from the string
    	_subPrefix = _subPrefix.substr(0, pos);
    }

    /** \brief set the group prefix to a new value
     *  \param prefix the prefix to set to
     *
     *  This overrides any value currently stored for the prefix
     */
    void setPrefix(const std::string& prefix)
    {
    	_subPrefix = prefix;
    }

    std::string& operator[](const std::string& key)
    {
    	return ParameterTree::operator[]((_subPrefix.empty() ? "" : _subPrefix + ".") + key);
    }

    const std::string& operator[](const std::string& key) const
    {
    	return ParameterTree::operator[]((_subPrefix.empty() ? "" : _subPrefix + ".") + key);
    }

  private:
    std::string _filename;
    std::string _subPrefix;
  };

} // namespace Dune

#endif //DUNE_COMMON_OUTPUTTREE_HH

#include<config.h>

#include<dune/common/parametertree.hh>
#include<dune/common/parametertreeparser.hh>
#include<dune/grid/yaspgrid.hh>

#include"../gridconstruction.hh"
int main()
{
  Dune::ParameterTree tree;
  Dune::ParameterTreeParser::readINITree("test.ini", tree);

  typedef Dune::YaspGrid<2> G1;
  typedef IniGridFactory<G1> F1;
  F1 factory(tree);

  return 0;
}

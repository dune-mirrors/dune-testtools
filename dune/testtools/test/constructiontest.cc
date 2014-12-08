#include<config.h>

#include<dune/common/parametertree.hh>
#include<dune/common/parametertreeparser.hh>
#include<dune/grid/uggrid.hh>
#include<dune/grid/yaspgrid.hh>

#include"../gridconstruction.hh"

int main()
{
  Dune::ParameterTree tree1, tree2, tree3;
  Dune::ParameterTreeParser::readINITree("test1.ini", tree1);
  Dune::ParameterTreeParser::readINITree("test2.ini", tree2);
  Dune::ParameterTreeParser::readINITree("test3.ini", tree3);

  typedef Dune::YaspGrid<2> G1;
  typedef Dune::YaspGrid<2, Dune::EquidistantOffsetCoordinates<double, 2> > G2;
  typedef Dune::YaspGrid<2, Dune::TensorProductCoordinates<double, 2> > G3;
  typedef Dune::UGGrid<2> G4;

  typedef IniGridFactory<G1> F1;
  typedef IniGridFactory<G2> F2;
  typedef IniGridFactory<G3> F3;
  typedef IniGridFactory<G4> F4;

  F1 factory1(tree1);
  std::cout << "Created YaspGrid with " << factory1.getGrid()->size(0) << " cells." << std::endl;
  F2 factory2(tree1);
  std::cout << "Created YaspGrid with " << factory2.getGrid()->size(0) << " cells." << std::endl;
  F3 factory3(tree1);
  std::cout << "Created YaspGrid with " << factory3.getGrid()->size(0) << " cells." << std::endl;
  F4 factory4(tree1);
  std::cout << "Created UGGrid with " << factory4.getGrid()->size(0) << " cells." << std::endl;

  return 0;
}

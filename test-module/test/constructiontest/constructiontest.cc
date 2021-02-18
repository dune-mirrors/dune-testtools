#include<config.h>

#include<dune/common/parametertree.hh>
#include<dune/common/parametertreeparser.hh>
#include<dune/grid/uggrid.hh>
#include<dune/grid/yaspgrid.hh>

#include<dune/testtools/gridconstruction.hh>

void test_ini(std::string filename, const Dune::MPIHelper& mpiHelper) {

  std::cout << std::endl << "******** starting ini file: " << filename << std::endl;

  Dune::ParameterTree tree;
  Dune::ParameterTreeParser::readINITree(filename, tree);

  if (tree.hasSub("yaspgrid")) {
    typedef Dune::YaspGrid<2> G1;
    typedef Dune::YaspGrid<2, Dune::EquidistantOffsetCoordinates<double, 2> > G2;
    typedef Dune::YaspGrid<2, Dune::TensorProductCoordinates<double, 2> > G3;

    typedef IniGridFactory<G1> F1;
    typedef IniGridFactory<G2> F2;
    typedef IniGridFactory<G3> F3;

    F1 factory1(tree, "yaspgrid");
    std::cout << "Created YaspGrid with " << factory1.getGrid()->size(0) << " cells." << std::endl;
    F2 factory2(tree, "yaspgrid");
    std::cout << "Created YaspGrid with " << factory2.getGrid()->size(0) << " cells." << std::endl;
    F3 factory3(tree, "yaspgrid");
    std::cout << "Created YaspGrid with " << factory3.getGrid()->size(0) << " cells." << std::endl;
  }

  if (tree.hasSub("onedgrid")) {
    typedef Dune::OneDGrid G;
    typedef IniGridFactory<G> F;
    F factory(tree, "onedgrid");
    std::cout << "Created OneDGrid with " << factory.getGrid()->size(0) << " cells." << std::endl;
  }

#if HAVE_UG
  if (tree.hasSub("ug")) {
    typedef Dune::UGGrid<2> G4;
    typedef IniGridFactory<G4> F4;

    F4 factory4(tree, "ug");
    std::cout << "Created UGGrid with " << factory4.getGrid()->size(0) << " cells." << std::endl;
  }
#else
  if (tree.hasSub("ug"))
  {
    std::cout << "UGGrid construction skipped because UGGrid has not been found." << std::endl;
  }
#endif

#if HAVE_DUNE_ALUGRID
  if (tree.hasSub("alu")) {
    typedef Dune::ALUGrid<2, 2, Dune::simplex, Dune::nonconforming> G5;
    typedef IniGridFactory<G5> F5;
    F5 factory5(tree, "alu");
    std::cout << "Created ALUGrid with " << factory5.getGrid()->size(0) << " cells." << std::endl;

    // We test a simplical gmsh file, so no cuboid grid in that case
    if (!tree.hasKey("alu.gmshFile")) {
      typedef Dune::ALUGrid<2, 2, Dune::cube, Dune::nonconforming> G6;
      typedef IniGridFactory<G6> F6;
      F6 factory6(tree, "alu");
      std::cout << "Created ALUGrid with " << factory6.getGrid()->size(0) << " cells." << std::endl;
    }
  }
#endif
}


int main(int argc, char** argv)
{
  try {
    const auto& mpiHelper = Dune::MPIHelper::instance(argc, argv);

    test_ini("ini/alu_gmsh.ini", mpiHelper);
    test_ini("ini/alu_structured.ini", mpiHelper);

    test_ini("ini/ug_gmsh.ini", mpiHelper);
    test_ini("ini/ug_structured_quadrilateral.ini", mpiHelper);
    test_ini("ini/ug_structured_simplical.ini", mpiHelper);

    test_ini("ini/yasp.ini", mpiHelper);
    test_ini("ini/oned.ini", mpiHelper);
  } catch (Dune::Exception& e) {
    std::cerr << e << std::endl;
    return 1;
  } catch (...) {
    std::cerr << "Generic exception!" << std::endl;
    return 2;
  }
  return 0;
}

// a fake convergence test to check the functionality
// and demonstrate the interface

#include <dune/testtools/outputtree.hh>
#include <dune/common/parametertreeparser.hh>
#include <dune/common/parametertree.hh>

int main(int argc, char** argv)
{
    // read the given ini file
    Dune::ParameterTree params;
    std::string parameterFileName = argv[1];
    Dune::ParameterTreeParser::readINITree(argv[1], params);

    // get some keys
    int level = params.get<int>("grid.level");
    //////////////////////////////////////////////
    // here the programme could do grid refinement
    //////////////////////////////////////////////

    // construct the output tree with the parameter tree
    Dune::OutputTree outputTree(params);

    ////////////////////////////////////////////////////////////////
    // here would be the programme that calculates norm and hmax and
    // outputs it like this:
    ////////////////////////////////////////////////////////////////
    double norm_p = 1.0/(1<<level);
    double norm_v = 1.0/(1<<(2*level));
    double hmax = 1.0/(1<<level);

    outputTree.setConvergenceData(norm_p, hmax, "pressure");
    outputTree.setConvergenceData(norm_v, hmax, "velocity");

    return 0;
}

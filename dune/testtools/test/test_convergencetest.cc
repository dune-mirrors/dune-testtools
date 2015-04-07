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
	int level = std::stoi(params["Grid.Level"]);
	//////////////////////////////////////////////
	// here the programme could do grid refinement
	//////////////////////////////////////////////

	// construct the output tree with the right filename
	// this is important so the test script can find the output
	std::string outputName = params["__name"];
	outputName += ".";
    outputName += params["__output_extension"];
	Dune::OutputTree outputTree(outputName);

	////////////////////////////////////////////////////////////////
    // here would be the programme that calculates norm and hmax and
    // outputs it like this:
    ////////////////////////////////////////////////////////////////
	// TODO this needs to be more general (get keys from the ini file)
	outputTree["Norm"] = std::to_string(1.0/(1<<level));
    outputTree["HMax"] = std::to_string(1.0/(1<<level));
   
    return 0;
}

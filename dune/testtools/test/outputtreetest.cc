#include "../outputtree.hh"

int main()
{
	Dune::OutputTree tree("testtree.ini");

	tree["bla"] = "blabb";
	tree["bli"] = "blibb";
	tree["blo"] = "blobb";
	tree["blu"] = "blubb";

	return 0;
}

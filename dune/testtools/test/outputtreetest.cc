#include "../outputtree.hh"

int main()
{
	Dune::OutputTree tree("testtree.ini");

	tree["bla"] = "blabb";
	tree.setPrefix("1.2");
	tree["bli"] = "blibb";
	tree.popPrefix();
	tree["blo"] = "blobb";
	tree.pushPrefix("3");
	tree["blu"] = "blubb";

	return 0;
}

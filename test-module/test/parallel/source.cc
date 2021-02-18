#include"config.h"

int main()
{
#if HAVE_MPI
  return 0;
#else
#warning "You need to have MPI installed to run this test!"
  return 77;
#endif
}

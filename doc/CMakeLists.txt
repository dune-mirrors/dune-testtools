add_subdirectory("doxygen")

# add the technical documentation pdf
dune_add_latex_document(technical.tex FATHER_TARGET doc DEFAULT_PDF)

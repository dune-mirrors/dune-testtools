add_subdirectory(doxygen)
add_subdirectory(sphinx)

# add the technical documentation pdf
dune_add_latex_document(
    SOURCE technical.tex
    FATHER_TARGET doc
)

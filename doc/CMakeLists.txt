add_subdirectory(doxygen)
add_subdirectory(sphinx)

# add the technical documentation pdf
add_latex_document(SOURCE technical.tex)

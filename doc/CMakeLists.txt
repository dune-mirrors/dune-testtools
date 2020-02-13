add_subdirectory(doxygen)
add_subdirectory(sphinx)

# add the technical documentation pdf
add_latexmk_document(SOURCE technical.tex)

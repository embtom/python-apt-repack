file(READ "${INPUT}" content)
string(REGEX REPLACE "\n_+" "\n" content "${content}")
string(REGEX REPLACE "^_+" "" content "${content}")
file(WRITE "${OUTPUT}" "${content}")

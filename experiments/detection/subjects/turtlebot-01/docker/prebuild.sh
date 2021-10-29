# # ensure that the python environment is correctly configured
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
# eval "$(pyenv virtualenv-init -)"

## install necessary python packages
pip uninstall empy
pip install \
  empy==3.3.4 \
  numpy==1.16.6 \
  defusedxml==0.7.1 \
  netifaces==0.11.0

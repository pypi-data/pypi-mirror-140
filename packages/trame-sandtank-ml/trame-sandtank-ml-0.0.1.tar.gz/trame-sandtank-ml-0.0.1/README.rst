===========
Sandtank ML
===========

Interactive application blending ParFlow execution and AI models for validation


* Free software: BSD License


Installing
----------
Build and install the Vue components

.. code-block:: console

    cd vue-components
    npm i
    npm run build
    cd -

For the Python layer it is recommended to use conda to properly install the various ML packages.

macOS conda setup
^^^^^^^^^^^^^^^^^

.. code-block:: console

    brew install miniforge
    conda init zsh

venv creation for AI
^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    conda create --name sandtank-ml python=3.9
    conda activate sandtank-ml
    conda install "pytorch==1.9.1" -c pytorch
    conda install scipy "scikit-learn==0.24.2" "scikit-image==0.18.3" -c conda-forge # For XAITK

    # For development when inside repo
    pip install -e .

    # For testing (no need to clone repo)
    pip install trame-sandtank-ml

    # Build parflow for simulation execution
    ./dependencies/parflow/build.sh


Run the application

.. code-block:: console

    conda activate sandtank-ml
    source ./dependencies/parflow/activate.sh
    trame-sandtank-ml

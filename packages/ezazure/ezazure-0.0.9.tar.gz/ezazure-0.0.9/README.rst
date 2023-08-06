#################################################################
ezazure: Easy Azure interface for uploading and downloading files
#################################################################

Azure's python interface for uploading and downloading files is complicated and
unintutive. :code:`ezazure` provides an easy interface to these
functionalities. 

To get started, check out the `docs <https://lakes-legendaries.github.io/ezazure/>`_!

If you will be contributing to this repo, check out the `developer's guide
<https://lakes-legendaries.github.io/ezazure/dev.html>`_.

**********
Quickstart
**********

#. Install this package:

   .. code-block:: bash

      pip install ezazure

#. Put your Azure connection string and container name in a :code:`.ezazure` file:

   .. code-block:: yaml

      connection_str: AZURE_CONNECTION_STRING
      container: CONTAINER_NAME

#. Run from the command line either of the following:

   .. code-block:: bash

      python -m ezazure --upload FNAME
      python -m ezazure --download FNAME

#. :code:`ezazure` supports regex pattern matching:

   .. code-block:: bash

      python -m ezazure --download --regex FNAME.*
      python -m ezazure --upload --regex PATH/FNAME[0-9]+\.csv

#. You can also use this package as an API:

   .. code-block:: python

      from ezazure import Azure


      azure = Azure()
      azure.upload(fname)
      azure.download(fname)

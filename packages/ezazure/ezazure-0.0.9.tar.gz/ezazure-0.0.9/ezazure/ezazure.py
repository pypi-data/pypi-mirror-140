"""Easy Azure interface for uploading and downloading files"""

from __future__ import annotations

from os import listdir, remove
from os.path import basename, dirname, expanduser, isfile, join
import re

from azure.storage.blob import (
    BlobClient,
    BlobServiceClient,
    ContainerClient,
    ContentSettings,
)
import yaml


class Azure:
    """Easy Azure interface for uploading/downloading files

    Parameters
    ----------
    config_fname: str, optional, default='.ezazure'
        Configuration file, containing your azure connection string (which can
        be the actual connection string, or the name of a file that contains
        your connection string) and your azure container. Example:

        .. code-block:: yaml

           connection_str: ~/secrets/azure
           container: litmon-private

        :code:`container` is only the default storage container, and can be
        overwritten in the :meth:`upload` and :meth:`download` functions. If
        it's not provided in this file, then you must supply :code:`container`
        variable in :meth:`upload` and :meth:`download`.
    check: bool, optional, default=False
        If :code:`config_fname` cannot be read on :code:`__init__()`, and
        :code:`check==True`, then throw an error. (Otherwise, errors are only
        thrown on :meth:`upload` and :meth`download` calls.)

        By keeping :code:`check==False`, then you can have code that looks like
        this:

        .. code-block:: python

           from ezazure import Azure


           Azure().download(fname)

        and your code will succeed if:

        #. :code:`fname` exists locally (regardless of whether you have Azure
           credentials in your :code:`config_fname` file), or
        #. :code:`fname` exists on your cloud and you have Azure credentials in
           your :code:`config_fname` file.

        This provides a tight cloud integration that still works even if you
        don't have access to the cloud, but have the files locally.

    Attributes
    ----------
    client: azure.storage.blob.BlobServiceClient
        Client for interfacing with Azure
    """
    def __init__(
        self,
        /,
        config_fname: str = '.ezazure',
        *,
        check: bool = False,
    ):

        # save passed
        self._config_fname = config_fname
        self._check = check

        # check for configuration file
        if not isfile(config_fname):
            self.client = None
            self._container = None
            if check:
                self._check_connection()
            else:
                return

        # load configuration
        config = yaml.safe_load(open(config_fname, 'r'))

        # get default container
        self._container = (
            config['container']
            if 'container' in config
            else None
        )

        # get connection string
        connection_str = config['connection_str']
        if 'AccountKey' not in connection_str:
            connection_str = expanduser(connection_str)
            try:
                connection_str = \
                    open(connection_str, 'r').read().strip()
            except FileNotFoundError:
                raise FileNotFoundError(
                    'Unable to read Azure connection string from '
                    f'{connection_str}.'
                )

        # get account name
        self._account = \
            re.search(r'AccountName=([^;]*);', connection_str).group(1)

        # connect to Azure
        self.client = BlobServiceClient.from_connection_string(connection_str)

    def _check_connection(self):
        """Check connection to Azure

        Raises
        ------
        FileNotFoundError
            If :code:`config_fname` could not be found
        """
        if self.client is None:
            raise FileNotFoundError(
                f'ezazure.Azure() requires a {self._config_fname} file that '
                'contains your connection_str and container.'
            )

    def _get_container(self, /, container: str) -> str:
        """Get container name.

        If :code:`container` is not :code:`None`, then return
        :code:`container`. Otherwise, return :code:`container` from your
        :code:`config_fname` file.

        Parameters
        ----------
        container: str
            current container name

        Returns
        -------
        str
            container name

        Raises
        ------
        KeyError
            If :code:`container` is :code:`None` and there's no default
            container in your :code:`config_fname` file
        """
        if container is None:
            if self._container is None:
                raise KeyError(
                    f'No default container given in {self._config_fname} file.'
                )
            return self._container
        return container

    def download(
        self,
        /,
        file: str,
        *,
        container: str = None,
        regex: bool = False,
        replace: bool = False,
    ):
        """Download file from Azure

        Parameters
        ----------
        file: str
            file to download
        container: str, optional, default=None
            if supplied, download from this container (instead of default
            container listed in :code:`.ezazure`)
        regex: bool, optional, default=False
            treat :code:`file` as a regex expression. download all files that
            match. all files will be downloaded to the same directory.
        replace: bool, optional, default=False
            if :code:`dest/file` exists locally, then skip the download

        Raises
        ------
        FileNotFoundError
            If :code:`file` does not exist in Azure
        """

        # process regular expresion
        if regex:

            # get container
            container = self._get_container(container)

            # download each file that matches pattern
            [
                self.download(
                    file=join(dirname(file), _file),
                    container=container,
                    regex=False,
                    replace=replace,
                )
                for _file in self._get_listing(container=container)[0]
                if re.search(file, join(dirname(file), _file)) is not None
            ]

            # return to stop processing
            return

        # check if file exists
        if not replace and isfile(file):
            return

        # get container
        container = self._get_container(container)

        # check connection
        self._check_connection()

        # connect to Azure
        client: BlobClient = self.client.get_blob_client(
            container=container,
            blob=basename(file)
        )

        # check that azure blob exists
        if not client.exists():
            raise FileNotFoundError(f'{file} does not exist in Azure')

        # download file
        with open(file, 'wb') as f:
            client.download_blob().readinto(f)

    def upload(
        self,
        /,
        file: str,
        *,
        container: str = None,
        regex: bool = False,
        replace: bool = True,
        update_listing: bool = True,
    ):
        """Upload file to Azure

        Parameters
        ----------
        file: str
            file to upload. This file will be uploaded as
            :code:`basename(file)`. (I.e. it will NOT be uploaded to a
            directory within the container, but rather to the container root
            level.)
        container: str, optional, default=None
            if supplied, download from this container (instead of default
            container listed in :code:`.ezazure`)
        regex: bool, optional, default=False
            treat :code:`file` as a regex expression. upload all files that
            match. all files must be in the same directory.
        replace: bool, optional, default=True
            replace existing file on server if it exists
        update_listing: bool, optional, default=True
            if True, and if there is public access to :code:`container`, then
            update directory listing (with :meth:`_update_listing`) after
            uploading

        Raises
        ------
        FileNotFoundError
            If the file cannot be found locally
        """

        # get container
        container = self._get_container(container)

        # process regular expresion
        if regex:

            # get local files
            directory = dirname(file)
            if len(directory) == 0:
                directory = '.'
            dfiles = listdir(directory)

            # upload each file that matches pattern
            [
                self.upload(
                    file=join(directory, _file),
                    container=container,
                    regex=False,
                    replace=replace,
                    update_listing=False,
                )
                for _file in dfiles
                if re.search(file, join(directory, _file)) is not None
            ]

            # update listing
            if update_listing:
                self._update_listing(container=container)

            # return to stop processing
            return

        # check connection
        self._check_connection()

        # check that file exists
        if not isfile(file):
            raise FileNotFoundError(f'{file} does not exist locally')

        # connect to Azure
        client: BlobClient = self.client.get_blob_client(
            container=container,
            blob=basename(file),
        )

        # delete existing
        if client.exists():
            if replace:
                client.delete_blob()
            else:
                return

        # check if is html file
        ext = basename(file).rsplit('.')[-1]
        if ext == 'html':
            content_settings = ContentSettings(content_type='text/html')
        elif ext == 'css':
            content_settings = ContentSettings(content_type='text/css')
        else:
            content_settings = None

        # upload file
        with open(file, 'rb') as data:
            client.upload_blob(
                data,
                content_settings=content_settings,
            )

        # update directory listing
        if update_listing:
            self._update_listing(container=container)

    def _get_listing(self, /, container: str) -> tuple(list[str], bool):
        """Get list of files on server

        Parameters
        ----------
        container: str
            Download from this container

        Returns
        -------
        list[str]
            list of files
        bool
            whether container has public access
        """

        # generate client
        client: ContainerClient = self.client.get_container_client(
            container=container,
        )

        # check public access
        public_access = \
            client.get_container_properties()['public_access'] is not None

        # get file list
        return [file['name'] for file in client.list_blobs()], public_access

    def _update_listing(
        self,
        /,
        container: str,
        *,
        fname: str = 'directory.html'
    ):
        """Update the directory listing for the current container

        This creates a simple html page that provides links to all files in the
        container.

        If the container has no public access, then this function will do
        nothing.

        Parameters
        ----------
        container: str
            Download from this container
        fname: str, optional, default='directory.html'
            filename for directory listing
        """

        # get file list
        files, public_access = self._get_listing(container=container)

        # skip if no public access
        if not public_access:
            return

        # create html page
        container_url = \
            f'https://{self._account}.blob.core.windows.net/{container}'
        with open(fname, 'w') as fid:
            for file in files:
                if file == fname:
                    continue
                link = f"{container_url}/{file.replace(' ', r'%20')}"
                print(f'<a href={link}>{file}</a><br>', file=fid)

        # upload directory listing
        self.upload(
            fname,
            container=container,
            replace=True,
            update_listing=False
        )

        # clean up
        remove(fname)

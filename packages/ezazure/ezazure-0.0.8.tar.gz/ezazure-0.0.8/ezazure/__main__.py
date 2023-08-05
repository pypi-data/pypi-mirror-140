from argparse import ArgumentParser

from ezazure import Azure

if __name__ == '__main__':

    # parse arguments
    parser = ArgumentParser(
        description='Easy Azure interface for uploading/downloading files'
    )
    parser.add_argument(
        'file',
        help='file name to upload/download',
    )
    parser.add_argument(
        '-u',
        '--upload',
        action='store_true',
        required=False,
        help='upload file',
    )
    parser.add_argument(
        '-d',
        '--download',
        action='store_true',
        required=False,
        help='download file',
    )
    parser.add_argument(
        '--container',
        required=False,
        help='container name (if not supplied, use default)',
    )
    parser.add_argument(
        '--regex',
        action='store_true',
        default=None,
        required=False,
        help='Treat file parameter as a regular expression '
             '(upload/download all files that match)',
    )
    parser.add_argument(
        '--replace',
        type=bool,
        default=None,
        required=False,
        help='Replace existing file',
    )
    args = parser.parse_args()

    # create instance
    azure = Azure()

    # get action
    if args.upload == args.download:
        raise ValueError('You must choose to either upload or download')
    action = azure.upload if args.upload else azure.download

    # get kwargs
    kwargs = {
        key: value
        for key, value in vars(args).items()
        if value is not None
        and key != 'upload'
        and key != 'download'
    }

    # run action
    action(**kwargs)

# Copyright: (c) 2019, Jordan Borean (@jborean93) <jborean93@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)

import uuid

from smbprotocol.connection import Connection
from smbprotocol.session import Session
from smbprotocol.open import CreateDisposition, CreateOptions, DirectoryAccessMask, FileAttributes, \
    FileInformationClass, ImpersonationLevel, Open, ShareAccess
from smbprotocol.tree import TreeConnect


class FileEntry(object):

    def __init__(self, path, file_directory_info):
        self.name = file_directory_info['file_name'].value.decode('utf-16-le')
        self.path = r"%s\%s" % (path, self.name)
        self.ctime = file_directory_info['creation_time'].value
        self.atime = file_directory_info['last_access_time'].value
        self.wtime = file_directory_info['last_write_time'].value
        self.size = file_directory_info['allocation_size'].value
        self.attributes = file_directory_info['file_attributes'].value

        self.is_archive = self._flag_set(FileAttributes.FILE_ATTRIBUTE_ARCHIVE)
        self.is_compressed = self._flag_set(FileAttributes.FILE_ATTRIBUTE_COMPRESSED)
        self.is_directory = self._flag_set(FileAttributes.FILE_ATTRIBUTE_DIRECTORY)
        self.is_hidden = self._flag_set(FileAttributes.FILE_ATTRIBUTE_HIDDEN)
        self.is_normal = self._flag_set(FileAttributes.FILE_ATTRIBUTE_NORMAL)
        self.is_readonly = self._flag_set(FileAttributes.FILE_ATTRIBUTE_READONLY)
        self.is_reparse_point = self._flag_set(FileAttributes.FILE_ATTRIBUTE_REPARSE_POINT)
        self.is_system = self._flag_set(FileAttributes.FILE_ATTRIBUTE_SYSTEM)
        self.is_temporary = self._flag_set(FileAttributes.FILE_ATTRIBUTE_TEMPORARY)

    def _flag_set(self, attribute):
        return self.attributes & attribute == attribute


def _listdir(tree, path, pattern, recurse):
    full_path = tree.share_name
    if path != "":
        full_path += r"\%s" % path

    # We create a compound request that does the following;
    #     1. Opens a handle to the directory
    #     2. Runs a query on the directory to list all the files
    #     3. Closes the handle of the directory
    # This is done in a compound request so we send 1 packet instead of 3 at the expense of more complex code.
    directory = Open(tree, path)
    query = [
        directory.create(
            ImpersonationLevel.Impersonation,
            DirectoryAccessMask.FILE_LIST_DIRECTORY,
            FileAttributes.FILE_ATTRIBUTE_DIRECTORY,
            ShareAccess.FILE_SHARE_READ | ShareAccess.FILE_SHARE_WRITE,
            CreateDisposition.FILE_OPEN,
            CreateOptions.FILE_DIRECTORY_FILE,
            send=False
        ),
        directory.query_directory(
            pattern,
            FileInformationClass.FILE_DIRECTORY_INFORMATION,
            send=False
        ),
        directory.close(False, send=False)
    ]

    query_reqs = tree.session.connection.send_compound(
        [x[0] for x in query],
        tree.session.session_id,
        tree.tree_connect_id,
        related=True
    )

    # Process the result of the create and close request before parsing the files.
    query[0][1](query_reqs[0])
    query[2][1](query_reqs[2])

    # Parse the queried files and repeat if the entry is a directory and recurse=True. We ignore . and .. as they are
    # not directories inside the queried dir.
    entries = []
    ignore_entries = [".".encode('utf-16-le'), "..".encode('utf-16-le')]
    for file_entry in query[1][1](query_reqs[1]):
        if file_entry['file_name'].value in ignore_entries:
            continue

        fe = FileEntry(full_path, file_entry)
        entries.append(fe)

        if fe.is_directory and recurse:
            dir_path = r"%s\%s" % (path, fe.name) if path != "" else fe.name
            entries += _listdir(tree, dir_path, recurse)

    return entries


def smb_listdir(path, pattern='*', username=None, password=None, encrypt=True, recurse=False):
    """
    List the files and folders in an SMB path and it's attributes.

    :param path: The full SMB share to list, this should be \\server\share with an optional path added to the end.
    :param pattern: The glob-like pattern to filter out files, defaults to '*' which matches all files and folders.
    :param username: Optional username to use for authentication, required if Kerberos is not used.
    :param password: Optional password to use for authentication, required if Kerberos is not used.
    :param enrypt: Whether to use encryption or not, Must be set to False if using an older SMB Dialect.
    :param recurse: Whether to search recursively or just the top level.
    :return: A list of FileEntry objects
    """
    path_split = [e for e in path.split('\\') if e]

    if len(path_split) < 2:
        raise Exception("Path should specify at least the server and share to connect to.")

    server = path_split[0]
    share = path_split[1]
    share_path = "\\".join(path_split[2:]) if len(path_split) > 2 else ''

    conn = Connection(uuid.uuid4(), server)
    conn.connect()

    try:
        session = Session(conn, username=username, password=password, require_encryption=encrypt)
        session.connect()
        try:
            tree = TreeConnect(session, r"\\%s\%s" % (server, share))
            tree.connect()
            try:
                return _listdir(tree, share_path, pattern, recurse)
            finally:
                tree.disconnect()
        finally:
            session.disconnect()
    finally:
        conn.disconnect()


files = smb_listdir(r'\\server.domain.local\c$\folder')

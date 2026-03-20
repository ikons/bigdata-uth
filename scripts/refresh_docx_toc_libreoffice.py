from __future__ import print_function

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.connection import NoConnectException


def make_property(name, value):
    prop = PropertyValue()
    prop.Name = name
    prop.Value = value
    return prop


def resolve_soffice_executable():
    candidates = []
    program_dir = os.path.dirname(os.path.abspath(sys.executable))
    candidates.append(os.path.join(program_dir, 'soffice.exe'))
    candidates.append(os.path.join(program_dir, 'soffice'))

    for env_name in ('LIBREOFFICE_PROGRAM', 'UNO_PATH'):
        base_path = os.environ.get(env_name)
        if not base_path:
            continue
        candidates.append(os.path.join(base_path, 'soffice.exe'))
        candidates.append(os.path.join(base_path, 'soffice'))

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    raise RuntimeError('Could not locate the LibreOffice soffice executable.')


def bootstrap_libreoffice():
    soffice = resolve_soffice_executable()
    profile_dir = tempfile.mkdtemp(prefix='lo-docx-')
    pipe_name = 'uno{0}'.format(uuid.uuid4().hex)
    profile_url = uno.systemPathToFileUrl(profile_dir)
    command = [
        soffice,
        '-headless',
        '-invisible',
        '-nologo',
        '-nodefault',
        '-norestore',
        '-nolockcheck',
        '-nofirststartwizard',
        '-accept=pipe,name={0};urp;'.format(pipe_name),
        '-env:UserInstallation={0}'.format(profile_url),
    ]

    devnull = open(os.devnull, 'wb')
    process = subprocess.Popen(command, stdout=devnull, stderr=devnull)

    local_context = uno.getComponentContext()
    resolver = local_context.ServiceManager.createInstanceWithContext(
        'com.sun.star.bridge.UnoUrlResolver',
        local_context,
    )
    connect_string = 'uno:pipe,name={0};urp;StarOffice.ComponentContext'.format(pipe_name)

    last_error = None
    for _ in range(60):
        if process.poll() is not None:
            break
        try:
            context = resolver.resolve(connect_string)
            return process, devnull, profile_dir, context
        except NoConnectException as exc:
            last_error = exc
            time.sleep(0.5)

    devnull.close()
    try:
        if process.poll() is None:
            process.kill()
    except Exception:
        pass
    shutil.rmtree(profile_dir, ignore_errors=True)
    raise RuntimeError('Cannot connect to the LibreOffice headless server: {0}'.format(last_error))


def load_hidden_document(desktop, file_path):
    file_url = uno.systemPathToFileUrl(os.path.abspath(file_path))
    properties = (
        make_property('Hidden', True),
        make_property('ReadOnly', False),
    )
    return desktop.loadComponentFromURL(file_url, '_blank', 0, properties)


def update_document_content(document):
    updated_indexes = 0

    try:
        indexes = document.getDocumentIndexes()
        count = indexes.getCount()
        for index in range(count):
            indexes.getByIndex(index).update()
            updated_indexes += 1
    except Exception:
        pass

    try:
        text_fields = document.getTextFields()
        text_fields.refresh()
    except Exception:
        pass

    try:
        document.refresh()
    except Exception:
        pass

    return updated_indexes


def close_document(document):
    try:
        document.close(True)
        return
    except Exception:
        pass

    try:
        document.dispose()
    except Exception:
        pass


def refresh_file(desktop, file_path):
    document = None
    try:
        document = load_hidden_document(desktop, file_path)
        index_count = update_document_content(document)
        document.store()
        print('LibreOffice refreshed TOC for {0} (indexes: {1})'.format(file_path, index_count))
    finally:
        if document is not None:
            close_document(document)


def parse_args():
    parser = argparse.ArgumentParser(description='Refresh DOCX table of contents with LibreOffice.')
    parser.add_argument('files', nargs='+', help='DOCX files to refresh.')
    return parser.parse_args()


def main():
    args = parse_args()
    process = None
    devnull = None
    profile_dir = None
    desktop = None

    try:
        process, devnull, profile_dir, context = bootstrap_libreoffice()
        service_manager = context.ServiceManager
        desktop = service_manager.createInstanceWithContext('com.sun.star.frame.Desktop', context)

        for file_path in args.files:
            refresh_file(desktop, file_path)

        if desktop is not None:
            try:
                desktop.terminate()
            except Exception:
                pass

        if process is not None:
            try:
                process.wait(timeout=15)
            except Exception:
                pass

        return 0
    finally:
        if process is not None and process.poll() is None:
            try:
                process.kill()
            except Exception:
                pass

        if devnull is not None:
            try:
                devnull.close()
            except Exception:
                pass

        if profile_dir:
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())

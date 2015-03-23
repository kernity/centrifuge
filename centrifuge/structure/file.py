# coding: utf-8
# Copyright (c) Alexandr Emelin. MIT license.

import json
import uuid
from tornado.gen import coroutine, Return
from centrifuge.structure import BaseStorage


from tornado.options import define

define(
    "file", default='structure.json', help="Path to JSON file with structure configuration", type=str
)


def extract_obj_id(obj):
    return obj['_id']


class Storage(BaseStorage):

    NAME = "JSON file"

    def __init__(self, *args, **kwargs):
        super(Storage, self).__init__(*args, **kwargs)
        self.data = json.load(open(self.options.file, 'r'))

    def connect(self, callback=None):
        callback()

    @coroutine
    def project_list(self):
        projects = self.data.get('projects', [])
        raise Return((projects, None))

    @coroutine
    def namespace_list(self):
        namespaces = self.data.get('namespaces', [])
        raise Return((namespaces, None))

    @coroutine
    def project_create(self, secret_key, options, project_id=None):

        to_insert = (
            project_id or uuid.uuid4().hex,
            secret_key,
            json.dumps(options)
        )

        to_return = {
            '_id': to_insert[0],
            'secret_key': to_insert[1],
            'options': to_insert[2]
        }

        data = {
            "_id": project_id or uuid.uuid4().hex,
            'secret_key': secret_key,
        }
        data.update(options)
        self.data["projects"].append(data)
        raise Return(({}, None))

    @coroutine
    def project_edit(self, project, options):

        project_id = extract_obj_id(project),
        for proj in self.data.get('projects', []):
            if proj["_id"] == project_id:
                proj.update(options)
                break

        to_return = {
            '_id': extract_obj_id(project),
            'options': options
        }
        raise Return((to_return, None))

    @coroutine
    def regenerate_project_secret_key(self, project, secret_key):

        project_id = extract_obj_id(project),
        for obj in self.data.get('projects', []):
            if obj["_id"] == project_id:
                obj["secret_key"] = secret_key
                break

        raise Return((secret_key, None))

    @coroutine
    def project_delete(self, project):
        """
        Delete project. Also delete all related namespaces.
        """
        project_id = extract_obj_id(project)

        projects = self.data.get('projects', [])

        index_to_delete = None
        for index, obj in enumerate(self.data.get('projects', [])):
            if obj["_id"] == project_id:
                index_to_delete = index
                break

        if index_to_delete is not None:
            del projects[index_to_delete]

        raise Return((True, None))

    @coroutine
    def namespace_create(self, project, name, options, namespace_id=None):

        to_return = {
            '_id': namespace_id or uuid.uuid4().hex,
            'project_id': extract_obj_id(project),
            'name': name,
            'options': options
        }

        data = {
            '_id': namespace_id or uuid.uuid4().hex,
            'project_id': extract_obj_id(project),
            'name': name,
        }

        raise Return((to_return, None))

    @coroutine
    def namespace_edit(self, namespace, name, options):

        to_return = {
            '_id': extract_obj_id(namespace),
            'name': name,
            'options': options
        }

        raise Return((to_return, None))

    @coroutine
    def namespace_delete(self, namespace):

        namespace_id = extract_obj_id(namespace)
        namespaces = self.data.get('namespaces', [])

        index_to_delete = None
        for index, obj in enumerate(namespaces):
            if obj["_id"] == namespace_id:
                index_to_delete = index
                break

        if index_to_delete is not None:
            del namespaces[index_to_delete]

        raise Return((True, None))

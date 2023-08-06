# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Poser Report Views
"""

from __future__ import unicode_literals, absolute_import

import os

import six

from rattail.util import simple_error

import colander
from deform import widget as dfwidget
from webhelpers2.html import HTML, tags

from tailbone.views import MasterView


class PoserReportView(MasterView):
    """
    Master view for Poser reports
    """
    normalized_model_name = 'poserreport'
    model_title = "Poser Report"
    model_key = 'report_key'
    route_prefix = 'poser.reports'
    url_prefix = '/poser/reports'
    filterable = False
    pageable = False
    editable = False            # TODO: should allow this somehow?
    downloadable = True

    labels = {
        'report_key': "Poser Key",
    }

    grid_columns = [
        'report_key',
        'report_name',
        'description',
        'error',
    ]

    form_fields = [
        'report_key',
        'report_name',
        'description',
        'flavor',
        'include_comments',
        'module_file',
        'module_file_path',
        'error',
    ]

    def __init__(self, request):
        super(PoserReportView, self).__init__(request)
        app = self.get_rattail_app()
        self.poser_handler = app.get_poser_handler()

        # nb. pre-load all reports b/c all views potentially need
        # access to the data set
        self.data = self.get_data()

    def get_data(self, session=None):
        if hasattr(self, 'data'):
            return self.data

        try:
            return self.poser_handler.get_all_reports()

        except Exception as error:
            self.request.session.flash(simple_error(error), 'error')

            if not self.request.is_root:
                self.request.session.flash("You must become root in order "
                                           "to do Poser Setup.", 'error')
            else:
                link = tags.link_to("Poser Setup",
                                    self.request.route_url('poser_setup'))
                msg = HTML.literal("Please see the {} page.".format(link))
                self.request.session.flash(msg, 'error')
            return []

    def configure_grid(self, g):
        super(PoserReportView, self).configure_grid(g)

        g.sorters['report_key'] = g.make_simple_sorter('report_key', foldcase=True)
        g.sorters['report_name'] = g.make_simple_sorter('report_name', foldcase=True)

        g.set_renderer('error', self.render_report_error)

        g.set_sort_defaults('report_name')

        g.set_link('report_key')
        g.set_link('report_name')
        g.set_link('description')
        g.set_link('error')

        g.set_searchable('report_key')
        g.set_searchable('report_name')
        g.set_searchable('description')

        if self.request.has_perm('report_output.create'):
            g.more_actions.append(self.make_action(
                'generate', icon='arrow-circle-right',
                url=self.get_generate_url))

    def get_generate_url(self, report, i=None):
        if not report.get('error'):
            return self.request.route_url('generate_specific_report',
                                          type_key=report['report'].type_key)

    def render_report_error(self, report, field):
        error = report.get('error')
        if error:
            return HTML.tag('span', class_='has-background-warning', c=[error])

    def get_instance(self):
        report_key = self.request.matchdict['report_key']
        for report in self.get_data():
            if report['report_key'] == report_key:
                return report
        raise self.notfound()

    def get_instance_title(self, report):
        return report['report_name']

    def make_form_schema(self):
        return PoserReportSchema()

    def make_create_form(self):
        return self.make_form({})

    def save_create_form(self, form):
        self.before_create(form)

        report = self.poser_handler.make_report(
            form.validated['report_key'],
            form.validated['report_name'],
            form.validated['description'],
            flavor=form.validated['flavor'],
            include_comments=form.validated['include_comments'])

        return report

    def configure_form(self, f):
        super(PoserReportView, self).configure_form(f)
        report = f.model_instance

        # report_key
        f.set_default('report_key', 'cool_widgets')
        f.set_helptext('report_key', "Unique computer-friendly key for the report type.")
        if self.creating:
            f.set_validator('report_key', self.unique_report_key)

        # report_name
        f.set_default('report_name', "Cool Widgets Weekly")
        f.set_helptext('report_name', "Human-friendly display name for the report.")

        # description
        f.set_default('description', "How many cool widgets we come across each week")
        f.set_helptext('description', "Brief description of the report.")

        # flavor
        if self.creating:
            f.set_helptext('flavor', "Determines the type of sample code to generate.")
            flavors = self.poser_handler.get_supported_report_flavors()
            values = [(key, flavor['description'])
                      for key, flavor in six.iteritems(flavors)]
            f.set_widget('flavor', dfwidget.SelectWidget(values=values))
            f.set_validator('flavor', colander.OneOf(flavors))
            if flavors:
                f.set_default('flavor', list(flavors)[0])
        else:
            f.remove('flavor')

        # include_comments
        if not self.creating:
            f.remove('include_comments')

        # module_file
        if self.creating:
            f.remove('module_file')
        else:
            # nb. set this key as workaround for render method, which
            # expects object to have this field
            report['module_file'] = os.path.basename(report['module_file_path'])
            f.set_renderer('module_file', self.render_downloadable_file)

        # error
        if self.creating or not report.get('error'):
            f.remove('error')
        else:
            f.set_renderer('error', self.render_report_error)

    def unique_report_key(self, node, value):
        for report in self.get_data():
            if report['report_key'] == value:
                raise node.raise_invalid("Poser report key must be unique")

    def download_path(self, report, filename):
        return report['module_file_path']

    def delete_instance(self, report):
        self.poser_handler.delete_report(report['report_key'])

    def replace(self):
        app = self.get_rattail_app()
        report = self.get_instance()

        value = self.request.POST['replacement_module']
        tempdir = app.make_temp_dir()
        filepath = os.path.join(tempdir, os.path.basename(value.filename))
        with open(filepath, 'wb') as f:
            f.write(value.file.read())

        try:
            newreport = self.poser_handler.replace_report(report['report_key'],
                                                          filepath)
        except Exception as error:
            self.request.session.flash(simple_error(error), 'error')
        else:
            report = newreport
        finally:
            os.remove(filepath)
            os.rmdir(tempdir)

        return self.redirect(self.get_action_url('view', report))

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._poser_report_defaults(config)

    @classmethod
    def _poser_report_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        model_title = cls.get_model_title()

        # replace module
        config.add_tailbone_permission(permission_prefix,
                                       '{}.replace'.format(permission_prefix),
                                       "Upload replacement module for {}".format(model_title))
        config.add_route('{}.replace'.format(route_prefix),
                         '{}/replace'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='replace',
                        route_name='{}.replace'.format(route_prefix),
                        permission='{}.replace'.format(permission_prefix))


class PoserReportSchema(colander.MappingSchema):

    report_key = colander.SchemaNode(colander.String())

    report_name = colander.SchemaNode(colander.String())

    description = colander.SchemaNode(colander.String())

    flavor = colander.SchemaNode(colander.String())

    include_comments = colander.SchemaNode(colander.Bool())


def defaults(config, **kwargs):
    base = globals()

    PoserReportView = kwargs.get('PoserReportView', base['PoserReportView'])
    PoserReportView.defaults(config)


def includeme(config):
    defaults(config)

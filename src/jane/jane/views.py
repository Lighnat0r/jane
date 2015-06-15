# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.shortcuts import render_to_response
from django.template.context import RequestContext

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from jane.documents import models, views


@api_view(['GET'])
def rest_root(request, format=None):
    """
    The root of Jane's REST interface. From here you have access to three
    subsections:

    **/waveforms**
    <div style="margin-left: 50px; margin-right: 50px;">
    *Browseable read-only REST API to explore the waveform database of Jane
    on a per waveform trace basis. Likely of limited usability but maybe
    interesting for some use cases. Each resource maps to one trace
    including a plot and some meta information.*
    </div>

    **/documents**
    <div style="margin-left: 50px; margin-right: 50px;">
    *REST API to work with Jane's document database at the document level.
    You can browse the available documents and view its associated indices.
    It is furthermore possible to add new documents via ``POST`` and ``PUT``
    or delete documents including all indices and attachments with
    ``DELETE``. Indices are generated automatically upon uploading or
    modifying a document.*
    </div>

    **/document_indices**
    <div style="margin-left: 50px; margin-right: 50px;">
    *REST API to work with Jane's document database at the index level. Each
    REST resource is one index which can also be searched upon. You can
    furthermore add, modify, or delete attachments for each index with
    ``POST``, ``PUT``, or ``DELETE``. One cannot delete or modify
    individual indices as they are tied to a document. To add, modify, or
    delete a whole document including all associated indices and attachments,
    please work with the **/documents** endpoint.*
    </div>
    """
    if request.method == "GET":
        # Use OrderedDicts to force the order of keys. Is there a different
        # way to do this within DRF?
        waveforms = OrderedDict()
        waveforms["name"] = "waveforms"
        waveforms["url"] = reverse('rest_waveforms-list', request=request)
        waveforms["description"] = ("REST view of Jane's waveform database")

        documents = OrderedDict()
        documents["name"] = "documents"
        documents["url"] = reverse(views.documents_rest_root, request=request)
        documents["description"] = ("Jane's document database at the "
                                    "document level")

        document_indices = OrderedDict()
        document_indices["name"] = "document_indices"
        document_indices["url"] = reverse(views.documents_indices_rest_root,
                                          request=request)
        document_indices["description"] = (
            "Jane's document database at the index level")

        return Response([waveforms, documents, document_indices])


def index(request):
    options = {
        'host': request.build_absolute_uri('/')[:-1],
        }
    return render_to_response("index.html", options,
                              RequestContext(request))

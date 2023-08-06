from django.conf import settings
from django.db.models import F


from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from foledol.django.tools.table import Table, TableColumn
from foledol.django.utils import get_search, paginate, new_context

from ..models import Grid


class GridTables(Table):
    def __init__(self, rows):
        super().__init__(rows, [
            TableColumn('name', "Nom"),
            TableColumn('table', "Table", method="table_as_str")
        ])
        self.update = 'django:grid_update'
        self.create = 'django:grid_create'
        self.search = True


@login_required
@staff_member_required
def grid_list(request):
    context = new_context()
    context['base'] = settings.DEFAULT_SPACE + '/base.html'

    grids = Grid.objects.all()

    search = get_search(request).strip()
    if len(search) > 0:
        grids = Grid.objects.filter(name=search)
    context['search'] = search
    context['table'] = GridTables(paginate(request, context, grids))

    return render(request, 'grids.html', context)


def grid_renumber(grid):
    order = 10
    for column in grid.column_set.all().order_by('order'):
        if column.order != order:
            column.order = order
            column.save()
        order += 10







from rest_framework.pagination import PageNumberPagination


class BookPagination(PageNumberPagination):
    """Paginación opt-in: sin ?page la lista se devuelve completa.

    El enunciado pide paginación "opcional", de modo que la ausencia del
    parámetro no debe alterar la forma de la respuesta.
    """

    page_size_query_param = "page_size"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        if self.page_query_param not in request.query_params:
            return None
        return super().paginate_queryset(queryset, request, view)

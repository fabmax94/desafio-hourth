from django.http import JsonResponse
from django.shortcuts import render

from .services import get_data_group_by_product, convert_str_to_date


def extract_params(request):
    request_data = request.GET.dict()
    start_date = request_data.get("init_date")
    end_date = request_data.get("finish_date")

    start_date = convert_str_to_date(start_date) if start_date else None
    end_date = convert_str_to_date(end_date) if end_date else None

    return start_date, end_date


def struct_data(request):
    start_date, end_date = extract_params(request)

    result = get_data_group_by_product(start_date, end_date)
    return JsonResponse({"result": result})


def struct_data_html(request):
    start_date, end_date = extract_params(request)

    result = get_data_group_by_product(start_date, end_date)
    return render(request, "desafio_hourth/struct_data.html", {"result": result})

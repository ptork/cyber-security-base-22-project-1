from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Order

# A03:2021 – Injection
@login_required()
def index(request):
  # This function is vulnerable to SQL injection
  # because we're forming a string from user input (query parameters)
  # and sending that off to our database

  sql = "SELECT * FROM orders_order WHERE user_id = {}".format(request.user.id)

  if request.GET.get('status'):
    sql += " AND status = '{}'".format(request.GET.get('status'))

  orders = Order.objects.raw(sql)

  return render(request, 'index.html', { 'orders': orders })

from django.contrib import admin
from .models import InvestmentRecord


@admin.register(InvestmentRecord)
class InvestmentRecordAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'stock_name', 'buy_date', 'sell_date', 'net_profit', 'annual_return_rate')
    list_filter = ('transaction_type', 'stock_name')
    search_fields = ('stock_name',)

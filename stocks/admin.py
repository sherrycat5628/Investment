from django.contrib import admin
from .models import InvestmentRecord


@admin.register(InvestmentRecord)
class InvestmentRecordAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'stock_name', 'buy_date', 'sell_date', 'net_profit', 'annual_return_rate_percent')
    list_filter = ('transaction_type', 'stock_name')
    search_fields = ('stock_name',)

    def annual_return_rate_percent(self, obj):
        if obj.annual_return_rate is None:
            return "-"
        return f"{obj.annual_return_rate * 100:.2f}%"
    annual_return_rate_percent.short_description = '年化報酬率'

from django.contrib import admin
from .models import InvestmentRecord
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum


class StockNameFilter(admin.SimpleListFilter):
    title = _('股票名稱與總淨利')
    parameter_name = 'stock_name'

    def lookups(self, request, model_admin):
        stocks = InvestmentRecord.objects.values_list('stock_name', flat=True).distinct()
        lookups = []
        for stock in stocks:
            total = InvestmentRecord.objects.filter(stock_name=stock).aggregate(total_profit=Sum('net_profit'))['total_profit'] or 0
            lookups.append((stock, f"{stock}（總淨利：{total}）"))
        return lookups

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(stock_name=self.value())
        return queryset


@admin.register(InvestmentRecord)
class InvestmentRecordAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_type',
        'stock_name',
        'buy_price',
        'buy_date',
        'sell_date',
        'sell_amount',
        'net_profit',
        'annual_return_rate_percent',
    )
    list_filter = (StockNameFilter, 'stock_name', 'transaction_type')
    search_fields = ('stock_name',)

    def annual_return_rate_percent(self, obj):
        if obj.annual_return_rate is None:
            return "-"
        return f"{obj.annual_return_rate * 100:.2f}%"
    annual_return_rate_percent.short_description = '年化報酬率'

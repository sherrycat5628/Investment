import openpyxl
from django.contrib import admin
from django.db.models import Sum
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from .models import DividendRecord, InvestmentRecord, Stock


class StockNameFilter(admin.SimpleListFilter):
    title = _('股票名稱與總淨利')
    parameter_name = 'stock_name'

    def lookups(self, request, model_admin):
        stocks = InvestmentRecord.objects.values_list('stock__id', 'stock__name').distinct()
        lookups = []
        for stock_id, stock_name in stocks:
            total = (
                InvestmentRecord.objects
                .filter(stock_id=stock_id)
                .aggregate(total_profit=Sum('net_profit'))['total_profit']
                or 0
            )
            lookups.append((stock_id, f"{stock_name}（總淨利：{total}）"))
        return lookups

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(stock_id=self.value())
        return queryset


@admin.action(description="匯出選取的投資紀錄為 Excel")
def export_to_excel(modeladmin, request, queryset):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "投資紀錄"

    headers = [
        '交易類型', '股票名稱', '買進日期', '買進價格', '張數', '買進金額',
        '手續費率', '手續費', '總成本', '賣出日期', '賣出價',
        '淨利', '獲利率', '年化報酬率', '持有天數'
    ]
    ws.append(headers)

    for obj in queryset:
        ws.append([
            obj.transaction_type,
            obj.stock.name,
            obj.buy_date,
            obj.buy_price,
            obj.quantity,
            obj.buy_amount,
            obj.fee_rate,
            obj.fee_amount,
            obj.total_cost,
            obj.sell_date,
            obj.sell_amount,
            obj.net_profit,
            obj.profit_rate,
            obj.annual_return_rate,
            obj.holding_days,
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename=investment_records.xlsx'
    wb.save(response)
    return response


@admin.register(InvestmentRecord)
class InvestmentRecordAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_type',
        'stock',
        'buy_price',
        'buy_date',
        'sell_date',
        'sell_amount',
        'net_profit',
        'annual_return_rate_percent',
    )
    list_filter = (StockNameFilter, 'stock', 'transaction_type')
    search_fields = ('stock__name',)
    actions = [export_to_excel]

    def annual_return_rate_percent(self, obj):
        if obj.annual_return_rate is None:
            return "-"
        return f"{obj.annual_return_rate * 100:.2f}%"
    annual_return_rate_percent.short_description = '年化報酬率'

    # def total_dividend(self, obj):
    #     # 透過 related_name "dividends" 從 Stock 取得所有股利紀錄加總
    #     total = obj.stock.dividends.aggregate(total=Sum('total_dividend'))['total'] or 0
    #     return f"{total:.2f}"
    # total_dividend.short_description = '累積股利'


class StockDividendFilter(admin.SimpleListFilter):
    title = _('股票名稱與累積股利')
    parameter_name = 'stock_dividend'

    def lookups(self, request, model_admin):
        stocks = InvestmentRecord.objects.values_list('stock__id', 'stock__name').distinct()
        lookups = []
        for stock_id, stock_name in stocks:
            actual_income = (
                DividendRecord.objects
                .filter(stock_id=stock_id)
                .aggregate(total=Sum('actual_income'))['total']
                or 0
            )
            lookups.append((stock_id, f"{stock_name}（累積股利：{actual_income}）"))
        return lookups

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(id=self.value())
        return queryset


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_net_profit', 'total_dividend')
    list_filter = (StockDividendFilter,)

    def total_net_profit(self, obj):
        return obj.investments.aggregate(total=Sum('net_profit'))['total'] or 0
    total_net_profit.short_description = "總淨利"

    def total_dividend(self, obj):
        return obj.dividends.aggregate(total=Sum('total_dividend'))['total'] or 0
    total_dividend.short_description = "累積股利"

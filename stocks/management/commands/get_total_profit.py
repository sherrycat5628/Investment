from django.core.management.base import BaseCommand
from stocks.models import InvestmentRecord
from django.db.models import Sum


class Command(BaseCommand):
    help = "計算目前累積總利潤，或指定個股的總利潤"

    def add_arguments(self, parser):
        parser.add_argument(
            '--stock',
            type=str,
            help='指定要查詢的股票名稱'
        )

    def handle(self, *args, **options):
        stock = options.get('stock')

        queryset = InvestmentRecord.objects.all()
        if stock:
            queryset = queryset.filter(stock_name=stock)

        total_profit = queryset.aggregate(total=Sum('net_profit'))['total']

        if stock:
            self.stdout.write(f"股票【{stock}】的累積總利潤：{total_profit or 0}")
        else:
            self.stdout.write(f"所有股票的累積總利潤：{total_profit or 0}")

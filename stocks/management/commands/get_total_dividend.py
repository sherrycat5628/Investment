from django.core.management.base import BaseCommand
from django.db.models import Sum
from stocks.models import Stock


class Command(BaseCommand):
    help = "計算目前累積股利，或指定個股的累積股利"

    def add_arguments(self, parser):
        parser.add_argument(
            '--stock',
            type=str,
            help='指定要查詢的股票名稱'
        )

    def handle(self, *args, **options):
        stock_name = options.get('stock')

        if stock_name:
            stocks = Stock.objects.filter(name=stock_name)
        else:
            stocks = Stock.objects.all()

        total_dividend = 0
        for stock in stocks:
            total_dividend += stock.dividends.aggregate(total=Sum('actual_income'))['total'] or 0

        if stock_name:
            self.stdout.write(f"股票【{stock_name}】的累積股利：{total_dividend:.2f}")
        else:
            self.stdout.write(f"所有股票的累積股利：{total_dividend:.2f}")

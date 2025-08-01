from django.core.management.base import BaseCommand
from stocks.models import InvestmentRecord
from django.db.models import Sum


class Command(BaseCommand):
    help = "計算目前庫存的總成本"

    def handle(self, *args, **kwargs):
        total_cost_in_stock = InvestmentRecord.objects.filter(sell_date__isnull=True).aggregate(
            total=Sum('total_cost')
        )['total']
        self.stdout.write(f"目前庫存的總成本：{total_cost_in_stock or 0}")

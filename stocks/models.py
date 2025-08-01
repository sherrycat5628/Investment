from django.db import models


class InvestmentRecord(models.Model):
    transaction_id = models.IntegerField(max_length=100, unique=True, verbose_name="交易ID", default='default_id')
    TRANSACTION_CHOICES = [
        ('BUY', '買'),
        ('SELL', '賣'),
    ]

    transaction_type = models.CharField(
        max_length=10, choices=TRANSACTION_CHOICES, default='BUY', verbose_name="交易類型"
    )
    stock_name = models.CharField(max_length=100, verbose_name="股票名稱")
    buy_date = models.DateField(verbose_name="買進日期")
    buy_price = models.FloatField(verbose_name="買進價")
    quantity = models.IntegerField(verbose_name="張數")
    amount = models.FloatField(verbose_name="金額")
    fee_rate = models.FloatField(verbose_name="手續費率")
    fee_amount = models.FloatField(verbose_name="手續費金額")
    total_cost = models.FloatField(verbose_name="總成本")
    sell_date = models.DateField(null=True, blank=True, verbose_name="賣出日期")
    sell_price = models.FloatField(null=True, blank=True, verbose_name="賣出價")
    net_profit = models.FloatField(null=True, blank=True, verbose_name="淨利")
    profit_rate = models.FloatField(null=True, blank=True, verbose_name="獲利率")
    annual_return_rate = models.FloatField(null=True, blank=True, verbose_name="年化報酬率")
    holding_days = models.IntegerField(null=True, blank=True, verbose_name="持有天數")

    def __str__(self):
        sell_date_display = self.sell_date.strftime("%Y-%m-%d") if self.sell_date else "持有中"
        return f"{self.stock_name} {self.get_transaction_type_display()} ({self.buy_date} - {sell_date_display})"

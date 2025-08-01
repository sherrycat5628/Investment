import pandas as pd
from django.core.management.base import BaseCommand
from stocks.models import DividendRecord, Stock


class Command(BaseCommand):
    help = "Import dividend records from a local Excel file (second worksheet)"

    def add_arguments(self, parser):
        parser.add_argument('filepath', type=str, help='Path to the Excel file')
        parser.add_argument("--dry-run", action="store_true", help="Preview data without saving to the database.")

    def handle(self, *args, **kwargs):
        filepath = kwargs['filepath']
        dry_run = kwargs["dry_run"]
        self.stdout.write(f"📄 讀取 Excel 第二個工作表：{filepath}")

        try:
            df = pd.read_excel(filepath, sheet_name=1, engine='openpyxl')
        except Exception as e:
            self.stderr.write(f"❌ 無法讀取 Excel：{e}")
            return

        if dry_run:
            self.stdout.write("🔍 Dry-run 模式：顯示前 5 筆資料，不儲存。\n")
            self.stdout.write(df.head().to_string(index=False))
            return

        for idx, row in df.iterrows():
            try:
                stock_name = str(row.get('名稱')).strip() if pd.notnull(row.get('名稱')) else ''
                if not stock_name:
                    self.stdout.write(f"⏭️ 跳過第 {idx} 列：缺少股票名稱欄位")
                    continue

                stock_obj, _ = Stock.objects.get_or_create(name=stock_name)

                payout_date = pd.to_datetime(row['發放日期']).date()

                record, created = DividendRecord.objects.update_or_create(
                    stock=stock_obj,
                    payout_date=payout_date,
                    defaults={
                        'quantity': int(row['張數']),
                        'dividend_per_share': row['每股股利'],
                        'total_dividend': row['總股利'],
                        'actual_income': row['實際進帳'],
                        'fee': row['手續費'],
                    }
                )

                if created:
                    self.stdout.write(f"✅ 新增股利紀錄：{record}")
                else:
                    self.stdout.write(f"🔁 更新股利紀錄：{record}")

            except Exception as e:
                self.stderr.write(f"❌ 匯入第 {idx} 列時發生錯誤：{e}")
                # self.stderr.write(f"Row data: {row.to_dict()}")

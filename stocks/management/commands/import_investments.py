# stocks/management/commands/import_investments.py
import pandas as pd
from django.core.management.base import BaseCommand
from stocks.models import InvestmentRecord


class Command(BaseCommand):
    help = "Import investment records from a local Excel file"

    def add_arguments(self, parser):
        parser.add_argument('filepath', type=str, help='Path to the Excel file')

    def handle(self, *args, **kwargs):
        filepath = kwargs['filepath']
        self.stdout.write(f"Reading Excel file from: {filepath}")

        try:
            df = pd.read_excel(filepath, engine='openpyxl')
        except Exception as e:
            self.stderr.write(f"Error reading Excel file: {e}")
            return

        for idx, row in df.iterrows():
            try:
                transaction_type_raw = str(row.get('交易類型')).strip() if pd.notnull(row.get('交易類型')) else ''
                stock_name = str(row.get('名稱')).strip() if pd.notnull(row.get('名稱')) else ''

                if not transaction_type_raw or not stock_name:
                    self.stdout.write(f"Skipping row {idx}: missing 交易類型 or 名稱")
                    continue

                if transaction_type_raw == '庫存':
                    transaction_type = 'BUY'
                elif transaction_type_raw == '賣':
                    transaction_type = 'SELL'
                else:
                    self.stdout.write(f"Skipping row {idx}: unknown 交易類型 '{transaction_type_raw}'")
                    continue

                buy_date = pd.to_datetime(row['買進日期']).date()

                raw_id = row.get('交易ID')
                if pd.notnull(raw_id):
                    try:
                        transaction_id = str(int(float(str(raw_id).strip())))
                    except (ValueError, TypeError):
                        self.stdout.write(f"Skipping row {idx}: invalid 交易ID: {raw_id}")
                        continue
                else:
                    self.stdout.write(f"Skipping row {idx}: missing 交易ID")
                    continue

                record, created = InvestmentRecord.objects.get_or_create(
                    transaction_id=transaction_id,
                    defaults={
                        'transaction_type': transaction_type,
                        'stock_name': stock_name,
                        'buy_date': buy_date,
                        'buy_price': row['買進價'],
                        'quantity': int(row['張數']),
                        'buy_amount': row['金額'],
                        'fee_rate': row['手續費率'],
                        'fee_amount': row['手續費'],
                        'total_cost': row['總成本'],
                        'sell_date': pd.to_datetime(row['賣出日期']).date() if pd.notnull(row['賣出日期']) else None,
                        'sell_amount': row['賣出價'] if pd.notnull(row['賣出價']) else None,
                        'net_profit': row['淨利'] if pd.notnull(row['淨利']) else None,
                        'profit_rate': row['獲利率'] if pd.notnull(row['獲利率']) else None,
                        'annual_return_rate': row['年化報酬率'] if pd.notnull(row['年化報酬率']) else None,
                        'holding_days': int(row['持有天數']) if pd.notnull(row['持有天數']) else None,
                    }
                )
                if created:
                    self.stdout.write(f"Imported new record: {record}")
                else:
                    self.stdout.write(f"Row {idx}: Record already exists, skipped: {record}")

            except Exception as e:
                self.stderr.write(f"Error importing row {idx}: {e}")
                self.stderr.write(f"Row data: {row.to_dict()}")

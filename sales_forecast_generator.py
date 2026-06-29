#!/usr/bin/env python3
"""
Sales Forecast Generator

Focused version of the sales report generator that loads sales CSV data,
summarizes historical monthly revenue, and projects sales for the next 3 months.
"""

from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import pandas as pd


class SalesForecastGenerator:
    """Generate a simple 3-month sales forecast from monthly sales history."""

    REQUIRED_COLUMNS = [
        "date",
        "sales_amount",
        "quantity_sold",
        "product_name",
        "customer_id",
        "salesperson_id",
        "region",
    ]

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.data = None
        self.monthly_sales = None
        self.forecast = None

    def load_data(self, data_source: str) -> pd.DataFrame:
        """Load sales data from CSV and remove rows that cannot be analyzed."""
        data = pd.read_csv(data_source)

        missing_columns = [
            column for column in self.REQUIRED_COLUMNS if column not in data.columns
        ]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        data["date"] = pd.to_datetime(data["date"], errors="coerce")
        data["sales_amount"] = pd.to_numeric(data["sales_amount"], errors="coerce")
        data["quantity_sold"] = pd.to_numeric(data["quantity_sold"], errors="coerce")

        data = data.dropna(subset=["date", "sales_amount", "quantity_sold"])
        data = data[(data["sales_amount"] > 0) & (data["quantity_sold"] > 0)]
        data = data.sort_values("date").reset_index(drop=True)

        if data.empty:
            raise ValueError("No valid sales rows available after cleaning.")

        self.data = data
        return data

    def get_monthly_sales(self) -> pd.DataFrame:
        """Aggregate cleaned sales data into monthly revenue totals."""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        monthly_sales = (
            self.data.set_index("date")
            .resample("ME")["sales_amount"]
            .sum()
            .reset_index()
        )
        monthly_sales["month"] = monthly_sales["date"].dt.strftime("%Y-%m")
        monthly_sales = monthly_sales[["month", "sales_amount"]]

        self.monthly_sales = monthly_sales
        return monthly_sales

    def forecast_three_months(self) -> pd.DataFrame:
        """Forecast sales for the next 3 months using recent average growth."""
        if self.monthly_sales is None:
            self.get_monthly_sales()

        historical_sales = self.monthly_sales["sales_amount"]
        growth_rates = (
            historical_sales.pct_change()
            .replace([np.inf, -np.inf], np.nan)
            .dropna()
            .tail(3)
        )
        average_growth_rate = float(growth_rates.mean()) if not growth_rates.empty else 0

        if np.isnan(average_growth_rate):
            average_growth_rate = 0

        last_month = pd.Period(self.monthly_sales.iloc[-1]["month"], freq="M")
        projected_sales = float(historical_sales.iloc[-1])
        forecast_rows: List[Dict[str, Any]] = []

        for offset in range(1, 4):
            forecast_month = last_month + offset
            projected_sales = max(projected_sales * (1 + average_growth_rate), 0)
            forecast_rows.append(
                {
                    "month": str(forecast_month),
                    "forecast_sales_amount": round(projected_sales, 2),
                    "growth_rate_used": round(average_growth_rate, 4),
                }
            )

        self.forecast = pd.DataFrame(forecast_rows)
        return self.forecast

    def generate_report(self, output_path: str) -> str:
        """Write a text report containing historical sales and forecasted sales."""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        monthly_sales = self.get_monthly_sales()
        forecast = self.forecast_three_months()

        total_revenue = float(self.data["sales_amount"].sum())
        average_monthly_revenue = float(monthly_sales["sales_amount"].mean())
        start_date = self.data["date"].min().strftime("%Y-%m-%d")
        end_date = self.data["date"].max().strftime("%Y-%m-%d")

        report_lines = [
            "=" * 80,
            "SALES FORECAST REPORT",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Historical Date Range: {start_date} to {end_date}",
            f"Total Historical Revenue: ${total_revenue:,.2f}",
            f"Average Monthly Revenue: ${average_monthly_revenue:,.2f}",
            "",
            "FORECAST METHOD",
            "-" * 40,
            "Next 3 months are projected from the average of recent month-over-month sales growth.",
            "Forecast values are floored at zero to avoid negative revenue projections.",
            "",
            "HISTORICAL MONTHLY SALES",
            "-" * 40,
        ]

        for _, row in monthly_sales.iterrows():
            report_lines.append(f"{row['month']}: ${row['sales_amount']:,.2f}")

        report_lines.extend(["", "3-MONTH SALES FORECAST", "-" * 40])

        for _, row in forecast.iterrows():
            report_lines.append(
                f"{row['month']}: ${row['forecast_sales_amount']:,.2f} "
                f"(growth rate used: {row['growth_rate_used']:.2%})"
            )

        with open(output_path, "w", encoding="utf-8") as report_file:
            report_file.write("\n".join(report_lines))

        return output_path


def main():
    """Run the forecast generator against the sample sales data."""
    generator = SalesForecastGenerator()
    generator.load_data("sample_sales_data.csv")
    output_path = generator.generate_report("sales_forecast_report.txt")
    print(f"Sales forecast report generated: {output_path}")


if __name__ == "__main__":
    main()

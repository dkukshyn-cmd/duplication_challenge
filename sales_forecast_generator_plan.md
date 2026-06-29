# Sales Forecast Generator Plan

## Goal
Create a focused version of the sales report generator that adds 3-month sales forecasting without expanding the already large `sales_report_generator.py` workflow. The new script should keep the same CSV input format and produce a clear report with historical monthly sales, forecast values, and the forecasting assumptions used.

## What Should Change
- Keep the existing sales CSV validation requirements: `date`, `sales_amount`, `quantity_sold`, `product_name`, `customer_id`, `salesperson_id`, and `region`.
- Convert `date` to datetime and `sales_amount` / `quantity_sold` to numeric values.
- Remove invalid rows with missing, zero, or negative sales and quantity values.
- Aggregate historical revenue by calendar month.
- Forecast the next 3 months of sales from recent monthly revenue trends.
- Write a text report that separates historical sales, forecasted sales, and summary metrics.

## Forecasting Approach
1. Sort cleaned sales records by date.
2. Resample sales into monthly totals.
3. Calculate recent month-over-month revenue growth.
4. Use the average of the most recent growth rates as the projection rate.
5. Starting from the latest historical month, project one month at a time for 3 future months.
6. Prevent negative forecast values by flooring projections at zero.

## New Script Structure
- `SalesForecastGenerator`: Main class for loading data, forecasting, and writing reports.
- `load_data(data_source)`: Reads and validates the sales CSV.
- `get_monthly_sales()`: Produces historical monthly revenue totals.
- `forecast_three_months()`: Returns a DataFrame with the next 3 forecast months and projected revenue.
- `generate_report(output_path)`: Writes a plain text forecast report.
- `main()`: Optional local entry point using `sample_sales_data.csv`.

## Report Contents
- Generated timestamp.
- Historical data date range.
- Total historical revenue.
- Average monthly revenue.
- Forecast method description.
- Historical monthly sales table.
- 3-month sales forecast table.

## Success Criteria
- `sales_forecast_generator.py` can load `sample_sales_data.csv`.
- The script generates exactly 3 future monthly forecast rows.
- The output is easier to follow than modifying the monolithic report generator.
- The implementation follows this plan and keeps forecasting logic isolated from unrelated analytics.

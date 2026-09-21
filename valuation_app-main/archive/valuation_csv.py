import csv

def get_float(prompt):
	while True:
		try:
			return float(input(prompt))
		except ValueError:
			print("Please enter a valid number.")

def get_choice(prompt, valid_choices):
	while True:
		choice = input(prompt).strip().lower()
		if choice in valid_choices:
			return choice
		print(f"Please enter one of: {', '.join(valid_choices)}")

def simple_valuation(name, revenue, profit_margin, growth_rate, industry_multiple):
	"""Simple valuation using basic revenue multiple"""
	estimated_value = revenue * industry_multiple
	
	print(f"\n{'=' * 50}")
	print(f"{name} - Simple Valuation")
	print(f"{'=' * 50}")
	print(f"\nKey Metrics:")
	print(f"  Annual Revenue:        ${revenue:,.2f}")
	print(f"  Industry Multiple:     {industry_multiple}x")
	print(f"\n{'=' * 50}")
	print(f"Estimated Company Value: ${estimated_value:,.2f}")
	print(f"{'=' * 50}")
	
	return estimated_value

def sophisticated_valuation(name, revenue, profit_margin, growth_rate, industry_multiple, 
                           capex, tax_rate, discount_rate, terminal_growth, debt, cash):
	"""Advanced valuation using DCF, multiples, and risk-adjusted models"""
	
	# Calculate detailed financial metrics
	profit = revenue * (profit_margin / 100)
	tax = profit * (tax_rate / 100)
	nopat = profit - tax  # Net Operating Profit After Tax
	capex_amount = revenue * (capex / 100)
	free_cash_flow = nopat - capex_amount
	
	# DCF Valuation - Project 5 years of cash flows
	print(f"\n{'=' * 50}")
	print(f"{name} - Sophisticated Valuation Analysis")
	print(f"{'=' * 50}")
	
	projected_fcf = []
	dcf_value = 0
	current_revenue = revenue
	
	print("\nProjected Free Cash Flows (5-year projection):")
	for year in range(1, 6):
		current_revenue *= (1 + growth_rate / 100)
		year_profit = current_revenue * (profit_margin / 100)
		year_tax = year_profit * (tax_rate / 100)
		year_nopat = year_profit - year_tax
		year_capex = current_revenue * (capex / 100)
		year_fcf = year_nopat - year_capex
		
		discount_factor = 1 / ((1 + discount_rate / 100) ** year)
		pv_fcf = year_fcf * discount_factor
		dcf_value += pv_fcf
		
		projected_fcf.append(year_fcf)
		print(f"  Year {year}: ${year_fcf:,.2f} (PV: ${pv_fcf:,.2f})")
	
	# Terminal Value
	terminal_fcf = projected_fcf[-1] * (1 + terminal_growth / 100)
	
	# Prevent division by zero
	adjusted_terminal = terminal_growth
	if discount_rate <= terminal_growth:
		print(f"\n⚠️  Warning: Discount rate ({discount_rate}%) must be greater than terminal growth ({terminal_growth}%)")
		print("Using adjusted terminal growth for calculation.")
		adjusted_terminal = min(terminal_growth, discount_rate - 1)
	
	terminal_value = terminal_fcf / ((discount_rate - adjusted_terminal) / 100)
	pv_terminal_value = terminal_value / ((1 + discount_rate / 100) ** 5)
	
	dcf_enterprise_value = dcf_value + pv_terminal_value
	dcf_equity_value = dcf_enterprise_value + cash - debt
	
	# Comparable Company Analysis (Multiples)
	revenue_multiple_value = revenue * industry_multiple
	earnings_multiple = industry_multiple * 12  # Typical P/E ratio
	earnings_multiple_value = profit * earnings_multiple
	
	# Growth-adjusted multiple (PEG ratio approach)
	peg_ratio = 1.5  # Industry standard
	growth_adjusted_multiple = (growth_rate / 100) * peg_ratio * 100
	growth_adjusted_value = profit * growth_adjusted_multiple
	
	# Risk-adjusted valuation
	risk_factor = 1.0
	if growth_rate > 30:
		risk_factor = 0.85  # High growth = higher risk
	elif growth_rate > 15:
		risk_factor = 0.92
	
	if profit_margin < 10:
		risk_factor *= 0.90  # Low margins = risk
	
	# Weighted average of all methods
	final_valuation = (
		dcf_equity_value * 0.40 +
		revenue_multiple_value * 0.20 +
		earnings_multiple_value * 0.20 +
		growth_adjusted_value * 0.20
	) * risk_factor
	
	# Output detailed results
	print(f"\nKey Financial Metrics:")
	print(f"  Annual Revenue:        ${revenue:,.2f}")
	print(f"  Profit Margin:         {profit_margin:.2f}%")
	print(f"  Annual Profit:         ${profit:,.2f}")
	print(f"  Free Cash Flow:        ${free_cash_flow:,.2f}")
	print(f"  Growth Rate:           {growth_rate:.2f}%")
	print(f"  WACC (Discount Rate):  {discount_rate:.2f}%")
	print(f"  Tax Rate:              {tax_rate:.2f}%")
	
	print(f"\nValuation Methods:")
	print(f"  DCF Enterprise Value:  ${dcf_enterprise_value:,.2f}")
	print(f"    + Cash:              ${cash:,.2f}")
	print(f"    - Debt:              ${debt:,.2f}")
	print(f"  DCF Equity Value:      ${dcf_equity_value:,.2f}")
	print(f"  Revenue Multiple:      ${revenue_multiple_value:,.2f}")
	print(f"  Earnings Multiple:     ${earnings_multiple_value:,.2f}")
	print(f"  Growth-Adjusted:       ${growth_adjusted_value:,.2f}")
	
	print(f"\nRisk Adjustments:")
	print(f"  Risk Factor:           {risk_factor:.2f}x")
	print(f"  Terminal Value (PV):   ${pv_terminal_value:,.2f}")
	
	print(f"\n{'=' * 50}")
	print(f"Final Estimated Value:   ${final_valuation:,.2f}")
	print(f"{'=' * 50}")
	print(f"\nValuation Range:")
	print(f"  Conservative:          ${final_valuation * 0.75:,.2f}")
	print(f"  Base Case:             ${final_valuation:,.2f}")
	print(f"  Optimistic:            ${final_valuation * 1.25:,.2f}")
	print(f"{'=' * 50}")
	
	return final_valuation

def process_csv(filename):
	"""Read companies from CSV and run valuations"""
	results = []
	output_lines = []
	
	try:
		with open(filename, 'r') as file:
			reader = csv.DictReader(file)
			companies = list(reader)
			
		header = "=" * 50
		output_lines.append(header)
		output_lines.append(f"Processing {len(companies)} companies from {filename}")
		output_lines.append(header)
		
		print("=" * 50)
		print(f"Processing {len(companies)} companies from {filename}")
		print("=" * 50)
		
		for company in companies:
			name = company['name']
			model = company['model'].strip().lower()
			revenue = float(company['revenue'])
			profit_margin = float(company['profit_margin'])
			growth_rate = float(company['growth_rate'])
			industry_multiple = float(company['industry_multiple'])
			
			if model == 'simple':
				valuation = simple_valuation(name, revenue, profit_margin, growth_rate, industry_multiple)
				results.append({
					'name': name,
					'model': model,
					'revenue': revenue,
					'profit_margin': profit_margin,
					'growth_rate': growth_rate,
					'industry_multiple': industry_multiple,
					'valuation': valuation
				})
			elif model == 'sophisticated':
				capex = float(company['capex'])
				tax_rate = float(company['tax_rate'])
				discount_rate = float(company['discount_rate'])
				terminal_growth = float(company['terminal_growth'])
				debt = float(company['debt'])
				cash = float(company['cash'])
				
				valuation = sophisticated_valuation(
					name, revenue, profit_margin, growth_rate, industry_multiple,
					capex, tax_rate, discount_rate, terminal_growth, debt, cash
				)
				results.append({
					'name': name,
					'model': model,
					'revenue': revenue,
					'profit_margin': profit_margin,
					'growth_rate': growth_rate,
					'industry_multiple': industry_multiple,
					'capex': capex,
					'tax_rate': tax_rate,
					'discount_rate': discount_rate,
					'terminal_growth': terminal_growth,
					'debt': debt,
					'cash': cash,
					'valuation': valuation
				})
			else:
				print(f"\n⚠️  Unknown model '{model}' for {name}. Skipping.")
				continue
			
			print("\n" + "=" * 50)
			input("Press Enter to continue to next company...")
		
		# Summary
		summary_header = "\n" + "=" * 60
		summary_title = "VALUATION SUMMARY"
		summary_line = "=" * 60
		
		output_lines.append(summary_header)
		output_lines.append(summary_title)
		output_lines.append(summary_line)
		
		print("\n" + "=" * 60)
		print("VALUATION SUMMARY")
		print("=" * 60)
		
		for result in results:
			line = f"{result['name']:30} ({result['model']:13}): ${result['valuation']:,.2f}"
			output_lines.append(line)
			print(line)
		
		output_lines.append(summary_line)
		print("=" * 60)
		
		# Save to output file
		output_filename = filename.replace('.csv', '_results.txt')
		with open(output_filename, 'w') as out_file:
			out_file.write('\n'.join(output_lines))
		
		print(f"\n✓ Results saved to: {output_filename}")
		
		# Also save detailed results to CSV
		csv_output_filename = filename.replace('.csv', '_results.csv')
		with open(csv_output_filename, 'w', newline='') as csv_out:
			fieldnames = ['name', 'model', 'revenue', 'profit_margin', 'growth_rate', 'industry_multiple',
			             'capex', 'tax_rate', 'discount_rate', 'terminal_growth', 'debt', 'cash',
			             'valuation', 'valuation_conservative', 'valuation_optimistic']
			writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
			writer.writeheader()
			for result in results:
				writer.writerow({
					'name': result['name'],
					'model': result['model'],
					'revenue': result.get('revenue', ''),
					'profit_margin': result.get('profit_margin', ''),
					'growth_rate': result.get('growth_rate', ''),
					'industry_multiple': result.get('industry_multiple', ''),
					'capex': result.get('capex', ''),
					'tax_rate': result.get('tax_rate', ''),
					'discount_rate': result.get('discount_rate', ''),
					'terminal_growth': result.get('terminal_growth', ''),
					'debt': result.get('debt', ''),
					'cash': result.get('cash', ''),
					'valuation': f"{result['valuation']:.2f}",
					'valuation_conservative': f"{result['valuation'] * 0.75:.2f}",
					'valuation_optimistic': f"{result['valuation'] * 1.25:.2f}"
				})
		
		print(f"✓ CSV results saved to: {csv_output_filename}")
		
	except FileNotFoundError:
		print(f"Error: File '{filename}' not found.")
	except Exception as e:
		print(f"Error processing CSV: {e}")

def interactive_mode():
	"""Original interactive mode"""
	print("=" * 50)
	print("     Company Valuation Estimator")
	print("=" * 50)

	# Choose valuation type
	print("\nValuation Model Options:")
	print("  [1] Simple - Quick estimate using revenue multiples")
	print("  [2] Sophisticated - Detailed DCF and risk-adjusted analysis")

	model_choice = get_choice("\nChoose your model (1 or 2): ", ['1', '2'])

	# Gather basic information
	print("\n--- Basic Company Information ---")
	name = input("What is the name of the company? ")
	revenue = get_float("What is the company's annual revenue (in USD)? ")
	profit_margin = get_float("What is the company's profit margin (as a percentage, e.g., 20 for 20%)? ")
	growth_rate = get_float("What is the expected annual growth rate (as a percentage)? ")
	industry_multiple = get_float("What is the typical revenue multiple for this industry? (e.g., 2.5) ")

	# Run appropriate valuation
	if model_choice == '1':
		simple_valuation(name, revenue, profit_margin, growth_rate, industry_multiple)
	else:
		print("\n--- Additional Information for Sophisticated Analysis ---")
		capex = get_float("What is the annual capital expenditure (CapEx) as % of revenue? ")
		tax_rate = get_float("What is the effective tax rate (as a percentage)? ")
		discount_rate = get_float("What discount rate (WACC) should we use (as a percentage, e.g., 10)? ")
		terminal_growth = get_float("What is the terminal growth rate (as a percentage, e.g., 3)? ")
		debt = get_float("What is the total debt (in USD)? ")
		cash = get_float("What is the cash on hand (in USD)? ")
		
		sophisticated_valuation(name, revenue, profit_margin, growth_rate, industry_multiple,
		                       capex, tax_rate, discount_rate, terminal_growth, debt, cash)

# Main program
if __name__ == "__main__":
	print("=" * 60)
	print("     COMPANY VALUATION TOOL")
	print("=" * 60)
	print("\nMode Selection:")
	print("  [1] Interactive Mode - Enter data manually")
	print("  [2] CSV Mode - Process companies from CSV file")
	
	mode = get_choice("\nChoose mode (1 or 2): ", ['1', '2'])
	
	if mode == '1':
		interactive_mode()
	else:
		csv_file = input("\nEnter CSV filename (default: companies.csv): ").strip()
		if not csv_file:
			csv_file = "companies.csv"
		process_csv(csv_file)

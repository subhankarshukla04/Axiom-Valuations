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

def sophisticated_valuation(name, revenue, profit_margin, growth_rate, industry_multiple):
	"""Advanced valuation using DCF, multiples, and risk-adjusted models"""
	
	# Get additional inputs for sophisticated model
	print("\n--- Additional Information for Sophisticated Analysis ---")
	capex = get_float("What is the annual capital expenditure (CapEx) as % of revenue? ")
	tax_rate = get_float("What is the effective tax rate (as a percentage)? ")
	discount_rate = get_float("What discount rate (WACC) should we use (as a percentage, e.g., 10)? ")
	terminal_growth = get_float("What is the terminal growth rate (as a percentage, e.g., 3)? ")
	debt = get_float("What is the total debt (in USD)? ")
	cash = get_float("What is the cash on hand (in USD)? ")
	
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
	if discount_rate <= terminal_growth:
		print(f"\n⚠️  Warning: Discount rate ({discount_rate}%) must be greater than terminal growth ({terminal_growth}%)")
		print("Using default terminal growth of 2% for calculation.")
		terminal_growth = min(terminal_growth, discount_rate - 1)
	
	terminal_value = terminal_fcf / ((discount_rate - terminal_growth) / 100)
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

# Main program
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
	sophisticated_valuation(name, revenue, profit_margin, growth_rate, industry_multiple)

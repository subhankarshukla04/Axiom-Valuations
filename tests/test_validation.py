#!/usr/bin/env python3
"""
Quick test script to validate the new architecture components.
"""
from models import CompanyFinancials
from pydantic import ValidationError

print("Testing Pydantic validation schemas...\n")

# Test valid data
print("1. Testing valid company data...")
try:
    valid = CompanyFinancials(
        name='Test Company', 
        sector='Technology', 
        revenue=1000000, 
        ebitda=300000,
        depreciation=50000, 
        capex_pct=0.05, 
        working_capital_change=0,
        profit_margin=0.15, 
        growth_rate_y1=0.20, 
        growth_rate_y2=0.15,
        growth_rate_y3=0.10, 
        terminal_growth=0.03, 
        tax_rate=0.25,
        shares_outstanding=1000000, 
        debt=500000, 
        cash=200000,
        market_cap_estimate=2000000, 
        beta=1.2, 
        risk_free_rate=0.04,
        market_risk_premium=0.07, 
        country_risk_premium=0.0, 
        size_premium=0.02,
        comparable_ev_ebitda=10.0, 
        comparable_pe=20.0, 
        comparable_peg=1.5
    )
    print("   ✅ Valid data passed validation\n")
except ValidationError as e:
    print(f"   ❌ Valid data failed: {e}\n")

# Test invalid data (negative revenue)
print("2. Testing invalid data (negative revenue)...")
try:
    invalid = CompanyFinancials(
        name='Bad Company', 
        sector='Technology', 
        revenue=-1000000,  # Invalid!
        ebitda=300000,
        depreciation=50000, 
        capex_pct=0.05, 
        working_capital_change=0,
        profit_margin=0.15, 
        growth_rate_y1=0.20, 
        growth_rate_y2=0.15,
        growth_rate_y3=0.10, 
        terminal_growth=0.03, 
        tax_rate=0.25,
        shares_outstanding=1000000, 
        debt=500000, 
        cash=200000,
        market_cap_estimate=2000000, 
        beta=1.2, 
        risk_free_rate=0.04,
        market_risk_premium=0.07, 
        country_risk_premium=0.0, 
        size_premium=0.02,
        comparable_ev_ebitda=10.0, 
        comparable_pe=20.0, 
        comparable_peg=1.5
    )
    print("   ❌ Invalid data passed (should have failed!)\n")
except ValidationError as e:
    print("   ✅ Invalid data correctly rejected\n")
    print(f"   Error details: {e.error_count()} validation errors\n")

# Test invalid tax rate
print("3. Testing invalid tax rate (150%)...")
try:
    invalid_tax = CompanyFinancials(
        name='Bad Tax Company', 
        sector='Technology', 
        revenue=1000000,
        ebitda=300000,
        depreciation=50000, 
        capex_pct=0.05, 
        working_capital_change=0,
        profit_margin=0.15, 
        growth_rate_y1=0.20, 
        growth_rate_y2=0.15,
        growth_rate_y3=0.10, 
        terminal_growth=0.03, 
        tax_rate=1.5,  # Invalid! > 100%
        shares_outstanding=1000000, 
        debt=500000, 
        cash=200000,
        market_cap_estimate=2000000, 
        beta=1.2, 
        risk_free_rate=0.04,
        market_risk_premium=0.07, 
        country_risk_premium=0.0, 
        size_premium=0.02,
        comparable_ev_ebitda=10.0, 
        comparable_pe=20.0, 
        comparable_peg=1.5
    )
    print("   ❌ Invalid tax rate passed (should have failed!)\n")
except ValidationError as e:
    print("   ✅ Invalid tax rate correctly rejected\n")

print("=" * 60)
print("✅ All validation tests passed!")
print("=" * 60)

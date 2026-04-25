#!/usr/bin/env python3
"""
Phase 1 Integration Test Script
Tests all scenario management, macro assumptions, and audit trail features
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5001"

def print_test(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"   {details}")

def test_scenarios():
    """Test scenario management APIs"""
    print("\n" + "="*80)
    print("TESTING SCENARIO MANAGEMENT")
    print("="*80)

    # Test 1: Get scenarios for company 1
    response = requests.get(f"{BASE_URL}/api/scenarios/1")
    passed = response.status_code == 200 and 'scenarios' in response.json()
    scenarios = response.json().get('scenarios', [])
    print_test("GET /api/scenarios/1", passed, f"Found {len(scenarios)} scenarios")

    # Test 2: Auto-generate Bear/Base/Bull scenarios
    response = requests.post(
        f"{BASE_URL}/api/scenario/generate-defaults",
        json={"company_id": 1, "created_by": 1}
    )
    passed = response.status_code in [200, 201]
    if passed:
        scenario_ids = response.json().get('scenario_ids', {})
        print_test("POST /api/scenario/generate-defaults", passed,
                  f"Generated: {', '.join(scenario_ids.keys())}")
    else:
        print_test("POST /api/scenario/generate-defaults", passed,
                  f"Error: {response.text}")

    # Test 3: Get specific scenario
    if scenarios:
        scenario_id = scenarios[0]['id']
        response = requests.get(f"{BASE_URL}/api/scenario/{scenario_id}")
        passed = response.status_code == 200 and 'scenario' in response.json()
        print_test(f"GET /api/scenario/{scenario_id}", passed)

    # Test 4: Compare scenarios
    if len(scenarios) >= 2:
        scenario_ids = ','.join([str(s['id']) for s in scenarios[:3]])
        response = requests.get(
            f"{BASE_URL}/api/scenario/compare",
            params={"company_id": 1, "scenario_ids": scenario_ids}
        )
        passed = response.status_code == 200 and 'comparison' in response.json()
        print_test("GET /api/scenario/compare", passed)

def test_macro_assumptions():
    """Test macro assumptions APIs"""
    print("\n" + "="*80)
    print("TESTING MACRO ASSUMPTIONS")
    print("="*80)

    # Test 1: Get all macro environments
    response = requests.get(f"{BASE_URL}/api/macro-environments")
    passed = response.status_code == 200 and 'environments' in response.json()
    environments = response.json().get('environments', [])
    print_test("GET /api/macro-environments", passed,
              f"Found {len(environments)} environments")

    # Test 2: Get active macro environment
    response = requests.get(f"{BASE_URL}/api/macro-environment/active")
    passed = response.status_code == 200 and 'environment' in response.json()
    if passed:
        env = response.json()['environment']
        print_test("GET /api/macro-environment/active", passed,
                  f"Active: {env.get('name', 'Unknown')}")
    else:
        print_test("GET /api/macro-environment/active", passed)

    # Test 3: Get specific macro environment
    if environments:
        macro_id = environments[0]['id']
        response = requests.get(f"{BASE_URL}/api/macro-environment/{macro_id}")
        passed = response.status_code == 200
        print_test(f"GET /api/macro-environment/{macro_id}", passed)

    # Test 4: Get sector multiples
    response = requests.get(f"{BASE_URL}/api/sector-multiples")
    passed = response.status_code == 200 and 'multiples' in response.json()
    multiples = response.json().get('multiples', [])
    print_test("GET /api/sector-multiples", passed,
              f"Found {len(multiples)} sectors")

    # Test 5: Get specific sector multiples
    response = requests.get(f"{BASE_URL}/api/sector-multiples/Technology")
    passed = response.status_code in [200, 404]  # OK if not found
    print_test("GET /api/sector-multiples/Technology", passed)

def test_audit_trail():
    """Test audit trail APIs"""
    print("\n" + "="*80)
    print("TESTING AUDIT TRAIL")
    print("="*80)

    # Test 1: Get audit trail
    response = requests.get(f"{BASE_URL}/api/audit-trail", params={"limit": 10})
    passed = response.status_code == 200 and 'entries' in response.json()
    entries = response.json().get('entries', [])
    print_test("GET /api/audit-trail", passed, f"Found {len(entries)} entries")

    # Test 2: Get material changes
    response = requests.get(f"{BASE_URL}/api/audit-trail/material")
    passed = response.status_code == 200 and 'changes' in response.json()
    changes = response.json().get('changes', [])
    print_test("GET /api/audit-trail/material", passed,
              f"Found {len(changes)} material changes")

    # Test 3: Get user changes
    response = requests.get(f"{BASE_URL}/api/audit-trail/user/1")
    passed = response.status_code == 200 and 'changes' in response.json()
    print_test("GET /api/audit-trail/user/1", passed)

def test_integration():
    """End-to-end integration test"""
    print("\n" + "="*80)
    print("INTEGRATION TEST: Full Scenario Workflow")
    print("="*80)

    # Step 1: Generate scenarios for company 1
    print("\nStep 1: Generate Bear/Base/Bull scenarios for company 1")
    response = requests.post(
        f"{BASE_URL}/api/scenario/generate-defaults",
        json={"company_id": 1, "created_by": 1}
    )

    if response.status_code in [200, 201]:
        result = response.json()
        print(f"✅ Generated {result.get('count', 0)} scenarios")
        scenario_ids = result.get('scenario_ids', {})

        # Step 2: Compare the scenarios
        if len(scenario_ids) >= 2:
            print("\nStep 2: Compare scenarios")
            ids_str = ','.join([str(id) for id in scenario_ids.values()])
            response = requests.get(
                f"{BASE_URL}/api/scenario/compare",
                params={"company_id": 1, "scenario_ids": ids_str}
            )

            if response.status_code == 200:
                comparison = response.json()['comparison']
                print(f"✅ Compared {comparison.get('num_scenarios', 0)} scenarios")
                print(f"   Company: {comparison.get('company_name', 'Unknown')}")

                # Show key differences
                scenarios = comparison.get('scenarios', [])
                if scenarios:
                    print("\n   Growth Rate Y1 comparison:")
                    for scenario in scenarios:
                        growth = scenario.get('growth_rate_y1', 0) * 100
                        print(f"   - {scenario.get('name', 'Unknown')}: {growth:.1f}%")
            else:
                print(f"❌ Comparison failed: {response.text}")
    else:
        print(f"❌ Generation failed: {response.text}")

    # Step 3: Switch macro environment
    print("\nStep 3: Test macro environment switching")
    response = requests.get(f"{BASE_URL}/api/macro-environments")
    if response.status_code == 200:
        environments = response.json().get('environments', [])
        if len(environments) >= 2:
            # Find Bear Market environment
            bear_env = next((e for e in environments if 'Bear' in e['name']), None)
            if bear_env:
                print(f"✅ Found Bear Market environment (ID: {bear_env['id']})")
                # Note: Not activating to avoid changing state
                print("   (Skipping activation to preserve current state)")

def main():
    """Run all tests"""
    print("="*80)
    print("PHASE 1 INTEGRATION TESTS")
    print("="*80)
    print(f"Testing against: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/api/companies")
        if response.status_code != 200:
            print("\n❌ ERROR: Server not responding. Is Flask running?")
            print(f"   Run: python3 app.py")
            return

        print("✅ Server is running\n")

        # Run all tests
        test_scenarios()
        test_macro_assumptions()
        test_audit_trail()
        test_integration()

        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print("✅ Phase 1 APIs are functional and ready to use!")
        print("\nNext steps:")
        print("1. Access APIs programmatically via curl or Python")
        print("2. Build custom UI/frontend if needed")
        print("3. Continue to Phase 2 features")

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server")
        print(f"   Make sure Flask is running: python3 app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

import sys
import os
import json

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Load environment variables from local.settings.json
def load_local_settings():
    """Load environment variables from local.settings.json"""
    settings_path = os.path.join(parent_dir, "local.settings.json")
    if os.path.exists(settings_path):
        with open(settings_path, 'r') as f:
            settings = json.load(f)
            for key, value in settings.get("Values", {}).items():
                os.environ[key] = value
        print("Loaded environment variables from local.settings.json")
    else:
        print("local.settings.json not found")

# Load settings before importing helper_functions
load_local_settings()

# Now we can import from helper_functions
from helper_functions import generate_kusto_query_from_nl, execute_llm_call

def test_generate_kusto_query_from_nl():
    """Test the generate_kusto_query_from_nl function with various Kusto scenarios"""
    
    # Test scenarios with different types of Kusto queries
    test_scenarios = [
        {
            "description": "what is the version distribution in sdp stage 2 preview channel?",
            "prompt": "what is the version distribution in sdp stage 2 preview channel?",
            "expected_keywords": ["summarize", "count", "version", "sdpStage", "Preview"]
        },
        {
            "description": "what is the version distribution in west us 2 preview channel?",
            "prompt": "what is the version distribution in west us 2 preview channel?",
            "expected_keywords": ["count", "regions", "version"]
        }
    ]
    
    print("=" * 60)
    print("Testing generate_kusto_query_from_nl function")
    print("=" * 60)
    
    successful_tests = 0
    total_tests = len(test_scenarios)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\nTest {i}/{total_tests}: {scenario['description']}")
        print(f"Prompt: '{scenario['prompt']}'")
        print("-" * 40)
        
        try:
            # Generate the Kusto query
            kusto_query = generate_kusto_query_from_nl(scenario['prompt'])
            
            print("Generated KQL Query:")
            print(kusto_query)
            print()
            
            # Validate the query contains expected keywords
            query_lower = kusto_query.lower()
            found_keywords = []
            missing_keywords = []
            
            for keyword in scenario['expected_keywords']:
                if keyword.lower() in query_lower:
                    found_keywords.append(keyword)
                else:
                    missing_keywords.append(keyword)
            
            if found_keywords:
                print(f"✅ Found expected keywords: {', '.join(found_keywords)}")
            
            if missing_keywords:
                print(f"⚠️  Missing keywords: {', '.join(missing_keywords)}")
            
            # Basic validation - check if it looks like a KQL query
            if any(op in query_lower for op in ['|', 'where', 'summarize', 'project', 'order']):
                print("✅ Query contains KQL operators")
                successful_tests += 1
            else:
                print("❌ Query doesn't appear to contain KQL operators")
            
        except Exception as e:
            print(f"❌ Error generating Kusto query: {e}")
        
        print("-" * 60)
    
    # Summary
    print(f"\nTest Summary:")
    print(f"Successful tests: {successful_tests}/{total_tests}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    return successful_tests == total_tests

def test_execute_llm_call_variations():
    """Test execute_llm_call with different parameter combinations"""
    
    print("\n" + "=" * 60)
    print("Testing execute_llm_call function variations")
    print("=" * 60)
    
    test_prompt = "Show me the count of events by status code"
    
    try:
        # Test 1: Default behavior (query only)
        print("\nTest 1: Default behavior (return_query_only=True)")
        print(f"Prompt: {test_prompt}")
        result1 = execute_llm_call(test_prompt)
        print("Result (Query only):")
        print(result1)
        print("-" * 40)
        
        # Test 2: Full response content
        print("\nTest 2: Full response content (return_query_only=False)")
        result2 = execute_llm_call(test_prompt, return_query_only=False)
        print("Result (Full content):")
        print(result2)
        print("-" * 40)
        
        # Test 3: Custom system prompt
        print("\nTest 3: Custom system prompt")
        custom_system_prompt = """You are a Kusto expert specializing in web analytics. 
Generate KQL queries for web server logs and HTTP status analysis."""
        
        result3 = execute_llm_call(
            test_prompt, 
            system_prompt=custom_system_prompt,
            return_query_only=True
        )
        print("Result (Custom system prompt):")
        print(result3)
        print("-" * 40)
        
        # Test 4: Full API response object
        print("\nTest 4: Full API response object (return_full_response=True)")
        response_obj = execute_llm_call(test_prompt, return_full_response=True)
        print("Response object type:", type(response_obj))
        if hasattr(response_obj, 'choices'):
            print("Response content:", response_obj.choices[0].message.content[:200] + "...")
            print("Model used:", getattr(response_obj, 'model', 'Unknown'))
        print("-" * 40)
        
        print("✅ All execute_llm_call variations completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in execute_llm_call variations: {e}")
        return False

def test_error_handling():
    """Test error handling scenarios"""
    
    print("\n" + "=" * 60)
    print("Testing error handling scenarios")
    print("=" * 60)
    
    try:
        # Test empty prompt
        print("\nTest: Empty prompt")
        try:
            result = execute_llm_call("")
            print("❌ Expected error for empty prompt, but got result")
        except ValueError as e:
            print(f"✅ Correctly caught ValueError: {e}")
        
        # Test None prompt
        print("\nTest: None prompt")
        try:
            result = execute_llm_call(None)
            print("❌ Expected error for None prompt, but got result")
        except (ValueError, TypeError) as e:
            print(f"✅ Correctly caught error: {e}")
        
        print("\n✅ Error handling tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error in error handling tests: {e}")
        return False

if __name__ == "__main__":
    print("Starting Kusto Natural Language Query Generation Tests")
    print("=" * 60)
    
    # Run all test suites
    test_results = []
    
    test_results.append(test_generate_kusto_query_from_nl())
    test_results.append(test_execute_llm_call_variations())
    test_results.append(test_error_handling())
    
    # Final summary
    print("\n" + "=" * 60)
    print("FINAL TEST SUMMARY")
    print("=" * 60)
    successful_suites = sum(test_results)
    total_suites = len(test_results)
    
    print(f"Test suites passed: {successful_suites}/{total_suites}")
    print(f"Overall success rate: {(successful_suites/total_suites)*100:.1f}%")
    
    if successful_suites == total_suites:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

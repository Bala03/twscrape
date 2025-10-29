#!/usr/bin/env python3
"""
Example script demonstrating Rettiwt-API integration with twscrape.

This example shows how to use the enhanced features while maintaining
backward compatibility with existing twscrape functionality.
"""

import asyncio
import json
from pathlib import Path

# Import enhanced API
import sys
sys.path.insert(0, str(Path(__file__).parent / "twscrape"))

try:
    from twscrape.enhanced_api import EnhancedAPI  
    from twscrape.accounts_pool import AccountsPool
    from twscrape.logger import set_log_level
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure twscrape dependencies are installed.")
    sys.exit(1)


async def demo_basic_functionality():
    """Demonstrate basic enhanced API functionality."""
    print("=== Basic Enhanced API Demo ===")
    
    # Initialize with in-memory database for demo
    pool = AccountsPool(db_file=":memory:", debug=True)
    api = EnhancedAPI(pool, debug=True, enable_rettiwt=True)
    
    # Check capabilities
    print("Checking enhanced capabilities...")
    capabilities = await api.get_enhanced_capabilities()
    
    print(f"✓ Rettiwt enabled: {capabilities.get('rettiwt_enabled')}")
    print(f"  Auth type: {capabilities.get('auth_type', 'none')}")
    print(f"  Available features: {len(capabilities.get('capabilities', []))}")
    
    # Show first few features
    features = capabilities.get('capabilities', [])
    if features:
        print("  Sample features:")
        for feature in features[:5]:
            print(f"    - {feature}")
        if len(features) > 5:
            print(f"    ... and {len(features) - 5} more")
    
    return True


async def demo_account_management():
    """Demonstrate account and API key management."""
    print("\n=== Account Management Demo ===")
    
    pool = AccountsPool(db_file=":memory:", debug=True)
    
    # Add a demo account (won't be functional without real credentials)
    print("Adding demo account...")
    await pool.add_account(
        username="demo_user",
        password="demo_pass", 
        email="demo@example.com",
        email_password="demo_email_pass",
        user_agent="Mozilla/5.0 Demo Agent"
    )
    
    # Demonstrate API key management (with fake key)
    print("Setting demo API key...")
    fake_api_key = "demo_api_key_" + "x" * 50
    
    # Set API key without validation for demo
    success = await pool.set_api_key("demo_user", fake_api_key, validate=False)
    print(f"✓ API key set: {success}")
    
    # Get account info
    account = await pool.get_account("demo_user")
    if account:
        print(f"✓ Account retrieved: {account.username}")
        print(f"  Has API key: {bool(account.api_key)}")
        print(f"  API key valid: {account.api_key_valid}")
    
    return True


async def demo_backward_compatibility():
    """Demonstrate that existing twscrape functionality still works."""
    print("\n=== Backward Compatibility Demo ===")
    
    pool = AccountsPool(db_file=":memory:")
    
    # Use regular API (non-enhanced)
    try:
        from twscrape.api import API
        api = API(pool, debug=True)
        print("✓ Regular API still works")
    except Exception as e:
        print(f"✗ Regular API failed: {e}")
        return False
    
    # Use enhanced API with Rettiwt disabled
    try:
        enhanced_api = EnhancedAPI(pool, enable_rettiwt=False)
        print("✓ Enhanced API with Rettiwt disabled works")
    except Exception as e:
        print(f"✗ Enhanced API failed: {e}")
        return False
    
    return True


async def main():
    """Run all demos."""
    set_log_level("INFO")
    
    print("Rettiwt-API Integration Demo")
    print("=" * 40)
    
    try:
        # Run demos
        demo1 = await demo_basic_functionality()
        demo2 = await demo_account_management() 
        demo3 = await demo_backward_compatibility()
        
        if demo1 and demo2 and demo3:
            print("\n🎉 All demos completed successfully!")
            print("\nNext steps:")
            print("1. Install Node.js 20+ if not already installed")
            print("2. Add real Twitter accounts: twscrape add_accounts file.txt format")
            print("3. Login accounts: twscrape login_accounts")
            print("4. Get Rettiwt API key using browser extension")
            print("5. Set API key: twscrape set_api_key username API_KEY")
            print("6. Enjoy enhanced features!")
            return 0
        else:
            print("\n❌ Some demos failed.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
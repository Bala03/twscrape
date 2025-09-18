#!/usr/bin/env python3
"""
Test script for validating the Rettiwt bridge functionality.

This script tests the basic integration between twscrape and Rettiwt-API
without requiring full authentication.
"""

import asyncio
import sys
import os

# Add the twscrape module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from twscrape.rettiwt_bridge import RettiwtBridge
from twscrape.logger import logger, set_log_level


async def test_bridge_basic():
    """Test basic bridge functionality."""
    print("=== Testing Rettiwt Bridge ===")
    
    try:
        # Initialize bridge
        bridge = RettiwtBridge(debug=True)
        print(f"✓ Bridge initialized with Node.js at: {bridge.node_path}")
        
        # Test dependency installation
        await bridge.ensure_dependencies()
        print("✓ Dependencies installed/verified")
        
        # Test guest key generation
        guest_key = await bridge.generate_guest_key()
        print(f"✓ Guest key generated: {guest_key[:20]}...")
        
        # Test supported features
        guest_features = await bridge.get_supported_features()
        print(f"✓ Guest features available: {len(guest_features)}")
        for feature in guest_features[:5]:  # Show first 5
            print(f"  - {feature}")
        
        print("\n=== Bridge Test Successful ===")
        return True
        
    except Exception as e:
        print(f"✗ Bridge test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_enhanced_api():
    """Test enhanced API functionality."""
    print("\n=== Testing Enhanced API ===")
    
    try:
        from twscrape.enhanced_api import EnhancedAPI
        from twscrape.accounts_pool import AccountsPool
        
        # Create a test pool (in-memory database)
        pool = AccountsPool(db_file=":memory:", debug=True)
        
        # Initialize enhanced API
        api = EnhancedAPI(pool, debug=True, enable_rettiwt=True)
        print("✓ Enhanced API initialized")
        
        # Test capabilities check
        capabilities = await api.get_enhanced_capabilities()
        print(f"✓ Capabilities retrieved: {capabilities.get('rettiwt_enabled')}")
        print(f"  Auth type: {capabilities.get('auth_type', 'none')}")
        print(f"  Features: {len(capabilities.get('capabilities', []))}")
        
        print("\n=== Enhanced API Test Successful ===")
        return True
        
    except Exception as e:
        print(f"✗ Enhanced API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    set_log_level("INFO")
    
    print("Twscrape Rettiwt Integration Test\n")
    
    # Test basic bridge functionality
    bridge_ok = await test_bridge_basic()
    
    # Test enhanced API
    api_ok = await test_enhanced_api()
    
    if bridge_ok and api_ok:
        print("\n🎉 All tests passed! Rettiwt integration is working.")
        return 0
    else:
        print("\n❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
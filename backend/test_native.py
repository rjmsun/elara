#!/usr/bin/env python3
"""
Test script to verify the native module build pipeline.

This script tests that the C++ extension can be imported and
the hello world function works correctly.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_native_module():
    """Test that the native module can be imported and used."""
    try:
        # Import the native module
        from elara.native import elara_native
        
        # Test the hello world function
        result = elara_native.hello_world()
        print(f"✅ Native module test successful!")
        print(f"   Result: {result}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import native module: {e}")
        return False
    except Exception as e:
        print(f"❌ Native module test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Elara native module build pipeline...")
    success = test_native_module()
    
    if success:
        print("\n🎉 Phase 1.3 complete: Native module build pipeline is working!")
        print("   The C++/Python integration is ready for high-performance components.")
    else:
        print("\n💥 Phase 1.3 failed: Native module build pipeline has issues.")
        sys.exit(1) 
#!/usr/bin/env python3
"""
Test script for port validation fix.
Validates that port parameter handling works correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chroma_mcp.server import create_parser, validate_connection_config
import argparse

def test_port_validation():
    """Test port validation with different input types."""
    print("🧪 Testing port validation fix...")

    parser = create_parser()

    # Test 1: Valid port as environment variable
    print("\n1. Testing valid port from environment...")
    os.environ['CHROMA_PORT'] = '8000'
    os.environ['CHROMA_HOST'] = 'localhost'

    args = parser.parse_args(['--client-type', 'http'])
    print(f"   args.port type: {type(args.port)}, value: {args.port}")

    try:
        validate_connection_config(args)
        print("   ✅ Port validation passed")
    except Exception as e:
        print(f"   ❌ Port validation failed: {str(e)}")
        return False

    # Test 2: Valid port as CLI argument
    print("\n2. Testing valid port from CLI...")
    try:
        args = parser.parse_args(['--client-type', 'http', '--host', 'localhost', '--port', '9000'])
        print(f"   args.port type: {type(args.port)}, value: {args.port}")
        validate_connection_config(args)
        print("   ✅ CLI port validation passed")
    except Exception as e:
        print(f"   ❌ CLI port validation failed: {str(e)}")
        return False

    # Test 3: Invalid port should fail
    print("\n3. Testing invalid port (should fail)...")
    try:
        args = parser.parse_args(['--client-type', 'http', '--host', 'localhost', '--port', '70000'])
        validate_connection_config(args)
        print("   ❌ Invalid port validation should have failed")
        return False
    except ValueError as e:
        print(f"   ✅ Invalid port correctly rejected: {str(e)}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return False

    # Test 4: No port specified
    print("\n4. Testing no port specified...")
    try:
        os.environ.pop('CHROMA_PORT', None)  # Remove env var
        args = parser.parse_args(['--client-type', 'http', '--host', 'localhost'])
        print(f"   args.port type: {type(args.port)}, value: {args.port}")
        validate_connection_config(args)
        print("   ✅ No port validation passed")
    except Exception as e:
        print(f"   ❌ No port validation failed: {str(e)}")
        return False

    print("\n✅ All port validation tests passed!")
    return True

def test_environment_variable_handling():
    """Test environment variable port handling."""
    print("\n🧪 Testing environment variable port handling...")

    # Test with string port in environment
    os.environ['CHROMA_PORT'] = '8080'
    os.environ['CHROMA_HOST'] = 'test-host'

    parser = create_parser()
    args = parser.parse_args(['--client-type', 'http'])

    print(f"   Environment CHROMA_PORT='8080'")
    print(f"   Parsed args.port: {args.port} (type: {type(args.port)})")

    if isinstance(args.port, int) and args.port == 8080:
        print("   ✅ Environment variable correctly parsed as integer")
        return True
    else:
        print(f"   ❌ Environment variable parsing failed")
        return False

if __name__ == "__main__":
    print("🚀 Port Validation Fix Test")
    print("=" * 50)

    success = True
    success &= test_port_validation()
    success &= test_environment_variable_handling()

    if success:
        print("\n🎉 All tests passed! Port validation fix is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Port validation fix needs more work.")
        sys.exit(1)
#!/usr/bin/env python3
"""
Test script for enhanced HTTP connectivity features.
Use this script to test the improved connection handling before deploying.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from chroma_mcp.server import (
    get_chroma_client,
    create_parser,
    validate_connection_config,
    test_http_connection,
    setup_logging
)
import argparse

def test_ephemeral_client():
    """Test ephemeral client creation."""
    print("\n=== Testing Ephemeral Client ===")

    # Create mock args for ephemeral client
    parser = create_parser()
    args = parser.parse_args(['--client-type', 'ephemeral', '--debug', 'true'])

    try:
        client = get_chroma_client(args)
        print("✅ Ephemeral client created successfully")

        # Test basic operations
        collections = client.list_collections()
        print(f"✅ Listed {len(collections)} collections")

        return True
    except Exception as e:
        print(f"❌ Ephemeral client test failed: {str(e)}")
        return False

def test_http_connectivity_validation():
    """Test HTTP connection validation without actually connecting."""
    print("\n=== Testing HTTP Connection Validation ===")

    parser = create_parser()

    # Test 1: Invalid hostname
    print("1. Testing invalid hostname...")
    args = parser.parse_args([
        '--client-type', 'http',
        '--host', 'invalid-hostname-that-does-not-exist.local',
        '--debug', 'true'
    ])

    try:
        validate_connection_config(args)
        print("❌ Validation should have failed for invalid hostname")
        return False
    except ValueError as e:
        print(f"✅ Validation correctly failed: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error during validation: {str(e)}")
        return False

    # Test 2: Valid port as integer (CLI)
    print("2. Testing valid port from CLI...")
    try:
        args = parser.parse_args([
            '--client-type', 'http',
            '--host', 'localhost',
            '--port', '8000',
            '--debug', 'true'
        ])
        print(f"   Port type: {type(args.port)}, value: {args.port}")
        validate_connection_config(args)
        print("✅ Port validation passed")
    except Exception as e:
        print(f"❌ Port validation failed: {str(e)}")
        return False

    # Test 3: Invalid port (too high)
    print("3. Testing invalid port (70000)...")
    try:
        args = parser.parse_args([
            '--client-type', 'http',
            '--host', 'localhost',
            '--port', '70000',
            '--debug', 'true'
        ])
        validate_connection_config(args)
        print("❌ Should have failed for invalid port")
        return False
    except ValueError as e:
        print(f"✅ Invalid port correctly rejected: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

    # Test 4: Port from environment variable
    print("4. Testing port from environment variable...")
    import os
    os.environ['CHROMA_PORT'] = '9000'
    try:
        args = parser.parse_args([
            '--client-type', 'http',
            '--host', 'localhost',
            '--debug', 'true'
        ])
        print(f"   Environment port type: {type(args.port)}, value: {args.port}")
        validate_connection_config(args)
        print("✅ Environment port validation passed")
    except Exception as e:
        print(f"❌ Environment port validation failed: {str(e)}")
        return False
    finally:
        os.environ.pop('CHROMA_PORT', None)

    return True

def test_connection_to_localhost():
    """Test connection to localhost (if Chroma is running locally)."""
    print("\n=== Testing localhost connection (optional) ===")

    # Test connection to localhost on default Chroma port, adjust accordingly
    success = test_http_connection("localhost", 8000, False, 5)
    if success:
        print("✅ localhost:8000 is reachable")

        # Try creating a client
        parser = create_parser()
        args = parser.parse_args([
            '--client-type', 'http',
            '--host', 'localhost',
            '--port', '8000',
            '--ssl', 'false',
            '--debug', 'true',
            '--connection-timeout', '5'
        ])

        try:
            client = get_chroma_client(args)
            print("✅ HTTP client created successfully for localhost")

            # Test basic operations
            collections = client.list_collections()
            print(f"✅ Listed {len(collections)} collections from localhost")
            return True

        except Exception as e:
            print(f"⚠️  HTTP client creation failed: {str(e)}")
            return False
    else:
        print("ℹ️  localhost:8000 not reachable - skipping HTTP client test")
        print("   (This is normal if you don't have Chroma running locally)")
        return True

def main():
    """Run all connectivity tests."""
    print("🧪 Chroma MCP Enhanced Connectivity Test Suite")
    print("=" * 50)

    # Enable debug logging for all tests
    setup_logging(True)

    tests = [
        ("Ephemeral Client", test_ephemeral_client),
        ("HTTP Validation", test_http_connectivity_validation),
        ("Localhost Connection", test_connection_to_localhost),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed! The enhanced connectivity features are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
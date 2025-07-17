#!/usr/bin/env python3
"""
Test connection script for Orca Job Orchestrator.
Tests SSH and WinRM connections to verify the connectors work.
"""

import asyncio
import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from connectors.ssh_connector import SSHConnector
from connectors.winrm_connector import WinRMConnector


async def test_ssh_connection():
    """Test SSH connection to Linux system from TESTUSER.md."""
    print("🐧 Testing SSH connection to Linux system...")
    print("=" * 50)
    
    # Test system details from TESTUSER.md
    hostname = '10.30.167.4'  # steve-tools
    username = 'testuser'
    password = 'hD1kBJ78VCyZawi'
    port = 22
    
    try:
        connector = SSHConnector(hostname, username, password, port)
        
        # Test connection
        result = await connector.test_connection()
        
        if result.success:
            print(f"✅ SSH connection successful!")
            print(f"   Response time: {result.response_time_ms:.2f} ms")
            if result.system_info:
                print(f"   Whoami output: {result.system_info.get('whoami_output', 'N/A')}")
        else:
            print(f"❌ SSH connection failed: {result.error_message}")
            
        # Test command execution
        if result.success:
            print("\n🔧 Testing command execution...")
            cmd_result = await connector.execute_command('whoami')
            
            if cmd_result.success:
                print(f"✅ Command executed successfully!")
                print(f"   Exit code: {cmd_result.exit_code}")
                print(f"   Output: {cmd_result.stdout.strip()}")
                print(f"   Duration: {cmd_result.duration_seconds:.2f} seconds")
            else:
                print(f"❌ Command execution failed: {cmd_result.error_message}")
                
        return result.success
        
    except Exception as e:
        print(f"❌ SSH test failed with exception: {e}")
        return False


async def test_winrm_connection():
    """Test WinRM connection to Windows system from TESTUSER.md."""
    print("\n🪟 Testing WinRM connection to Windows system...")
    print("=" * 50)
    
    # Test system details from TESTUSER.md
    hostname = '10.16.120.5'  # steve-desktop
    username = 'testuser'
    password = 'hD1kBJ78VCyZawi'
    port = 5985
    
    try:
        connector = WinRMConnector(hostname, username, password, port)
        
        # Test connection
        result = await connector.test_connection()
        
        if result.success:
            print(f"✅ WinRM connection successful!")
            print(f"   Response time: {result.response_time_ms:.2f} ms")
            if result.system_info:
                print(f"   Whoami output: {result.system_info.get('whoami_output', 'N/A')}")
        else:
            print(f"❌ WinRM connection failed: {result.error_message}")
            
        # Test command execution
        if result.success:
            print("\n🔧 Testing command execution...")
            cmd_result = await connector.execute_command('whoami')
            
            if cmd_result.success:
                print(f"✅ Command executed successfully!")
                print(f"   Exit code: {cmd_result.exit_code}")
                print(f"   Output: {cmd_result.stdout.strip()}")
                print(f"   Duration: {cmd_result.duration_seconds:.2f} seconds")
            else:
                print(f"❌ Command execution failed: {cmd_result.error_message}")
                
        return result.success
        
    except Exception as e:
        print(f"❌ WinRM test failed with exception: {e}")
        return False


async def main():
    """Main test function."""
    print("🐋 Orca Job Orchestrator Connection Test")
    print("=" * 60)
    print("Testing connections to systems from TESTUSER.md")
    print()
    
    # Test SSH connection
    ssh_success = await test_ssh_connection()
    
    # Test WinRM connection
    winrm_success = await test_winrm_connection()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 20)
    print(f"SSH (Linux):   {'✅ PASS' if ssh_success else '❌ FAIL'}")
    print(f"WinRM (Windows): {'✅ PASS' if winrm_success else '❌ FAIL'}")
    
    if ssh_success and winrm_success:
        print("\n🎉 All connection tests passed!")
        print("Orca is ready to manage both Linux and Windows systems.")
        return 0
    else:
        print("\n⚠️  Some connection tests failed.")
        print("Please check network connectivity and credentials.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
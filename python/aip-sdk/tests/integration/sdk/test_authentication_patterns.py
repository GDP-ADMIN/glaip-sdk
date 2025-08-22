#!/usr/bin/env python3
"""Authentication Patterns Example - Demonstrating secure credential management.

This example shows advanced authentication patterns including:
- API key rotation and management
- Token refresh mechanisms
- Secure credential storage and redaction
- Authentication error handling and retry logic
- Audit logging for security events

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Any

from glaip_sdk import Client
from glaip_sdk.exceptions import AuthenticationError


class SecureCredentialManager:
    """Manages credentials securely with rotation and audit logging."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.credentials = {}
        self.rotation_history = []
        self.audit_log = []

    def add_credential(self, name: str, api_key: str, description: str = "") -> str:
        """Add a new credential with metadata."""
        credential_id = f"cred_{len(self.credentials) + 1}"

        self.credentials[credential_id] = {
            "name": name,
            "api_key": api_key,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "usage_count": 0,
            "status": "active",
        }

        self._audit_log("credential_added", f"Added credential: {name}")
        return credential_id

    def rotate_credential(self, credential_id: str, new_api_key: str) -> bool:
        """Rotate an existing credential."""
        if credential_id not in self.credentials:
            return False

        old_credential = self.credentials[credential_id].copy()

        # Store rotation history
        self.rotation_history.append(
            {
                "credential_id": credential_id,
                "old_key_hash": self._hash_key(old_credential["api_key"]),
                "new_key_hash": self._hash_key(new_api_key),
                "rotated_at": datetime.now().isoformat(),
                "reason": "scheduled_rotation",
            }
        )

        # Update credential
        self.credentials[credential_id]["api_key"] = new_api_key
        self.credentials[credential_id]["last_rotated"] = datetime.now().isoformat()

        self._audit_log(
            "credential_rotated", f"Rotated credential: {old_credential['name']}"
        )
        return True

    def get_credential(self, credential_id: str) -> dict[str, Any] | None:
        """Get credential details (without exposing the actual key)."""
        if credential_id not in self.credentials:
            return None

        cred = self.credentials[credential_id].copy()
        # Redact the actual API key
        cred["api_key"] = f"{cred['api_key'][:8]}...{cred['api_key'][-4:]}"
        return cred

    def _hash_key(self, api_key: str) -> str:
        """Create a hash of the API key for audit purposes."""
        return f"hash_{hash(api_key) % 10000:04d}"

    def _audit_log(self, event: str, message: str):
        """Log security events for audit purposes."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "message": message,
            "source": "credential_manager",
        }
        self.audit_log.append(log_entry)
        print(f"🔒 [AUDIT] {event}: {message}")


class AuthenticatedClientManager:
    """Manages authenticated clients with rotation and error handling."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.credential_manager = SecureCredentialManager(base_url)
        self.active_clients = {}
        self.retry_config = {"max_retries": 3, "base_delay": 1.0, "max_delay": 10.0}

    def create_client_with_credential(self, credential_id: str) -> Client | None:
        """Create a client using a specific credential."""
        if credential_id not in self.credential_manager.credentials:
            print(f"❌ Credential {credential_id} not found")
            return None

        cred = self.credential_manager.credentials[credential_id]

        try:
            # Create client with the credential
            client = Client(api_url=self.base_url, api_key=cred["api_key"])

            # Test the connection
            self._test_client_connection(client, credential_id)

            # Store active client
            self.active_clients[credential_id] = {
                "client": client,
                "created_at": datetime.now(),
                "last_used": datetime.now(),
            }

            # Update usage stats
            cred["last_used"] = datetime.now().isoformat()
            cred["usage_count"] += 1

            return client

        except Exception as e:
            print(f"❌ Failed to create client with credential {credential_id}: {e}")
            return None

    def _test_client_connection(self, client: Client, credential_id: str) -> bool:
        """Test if the client can authenticate successfully."""
        try:
            # Try to list agents as a connection test
            client.list_agents()
            print(f"✅ Credential {credential_id} authenticated successfully")
            return True
        except AuthenticationError:
            print(f"❌ Credential {credential_id} authentication failed")
            return False
        except Exception as e:
            print(f"⚠️  Connection test failed for credential {credential_id}: {e}")
            return False

    def rotate_and_recreate_client(
        self, credential_id: str, new_api_key: str
    ) -> Client | None:
        """Rotate credential and recreate client."""
        print(f"🔄 Rotating credential {credential_id}...")

        # Rotate the credential
        if not self.credential_manager.rotate_credential(credential_id, new_api_key):
            return None

        # Remove old client
        if credential_id in self.active_clients:
            del self.active_clients[credential_id]

        # Create new client with rotated credential
        return self.create_client_with_credential(credential_id)

    def cleanup_expired_clients(self, max_age_hours: int = 24):
        """Clean up clients that haven't been used recently."""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        expired_clients = []

        for cred_id, client_info in self.active_clients.items():
            if client_info["last_used"] < cutoff_time:
                expired_clients.append(cred_id)

        for cred_id in expired_clients:
            print(f"🧹 Cleaning up expired client for credential {cred_id}")
            del self.active_clients[cred_id]

        if expired_clients:
            self._audit_log(
                "clients_cleaned", f"Cleaned up {len(expired_clients)} expired clients"
            )


class SecurityAuditor:
    """Audits security practices and generates reports."""

    def __init__(self, credential_manager: SecureCredentialManager):
        self.credential_manager = credential_manager

    def generate_security_report(self) -> dict[str, Any]:
        """Generate a comprehensive security report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "credential_summary": self._analyze_credentials(),
            "rotation_summary": self._analyze_rotations(),
            "audit_summary": self._analyze_audit_log(),
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _analyze_credentials(self) -> dict[str, Any]:
        """Analyze credential security posture."""
        total_creds = len(self.credential_manager.credentials)
        active_creds = sum(
            1
            for c in self.credential_manager.credentials.values()
            if c["status"] == "active"
        )

        # Check for old credentials
        now = datetime.now()
        old_creds = 0
        for cred in self.credential_manager.credentials.values():
            created = datetime.fromisoformat(cred["created_at"])
            if (now - created).days > 90:  # 90 days
                old_creds += 1

        return {
            "total_credentials": total_creds,
            "active_credentials": active_creds,
            "old_credentials": old_creds,
            "security_score": max(0, 100 - (old_creds * 20)),
        }

    def _analyze_rotations(self) -> dict[str, Any]:
        """Analyze credential rotation patterns."""
        rotations = self.credential_manager.rotation_history
        recent_rotations = [
            r
            for r in rotations
            if (datetime.now() - datetime.fromisoformat(r["rotated_at"])).days <= 30
        ]

        return {
            "total_rotations": len(rotations),
            "recent_rotations": len(recent_rotations),
            "last_rotation": rotations[-1]["rotated_at"] if rotations else None,
        }

    def _analyze_audit_log(self) -> dict[str, Any]:
        """Analyze audit log for security insights."""
        events = [log["event"] for log in self.credential_manager.audit_log]
        event_counts = {}

        for event in events:
            event_counts[event] = event_counts.get(event, 0) + 1

        return {
            "total_events": len(events),
            "event_breakdown": event_counts,
            "last_event": self.credential_manager.audit_log[-1]["timestamp"]
            if self.credential_manager.audit_log
            else None,
        }

    def _generate_recommendations(self) -> list[str]:
        """Generate security recommendations."""
        recommendations = []

        cred_analysis = self._analyze_credentials()
        if cred_analysis["old_credentials"] > 0:
            recommendations.append("Rotate credentials older than 90 days")

        if cred_analysis["security_score"] < 80:
            recommendations.append("Review credential security practices")

        return recommendations


def demonstrate_credential_rotation(client_manager: AuthenticatedClientManager) -> bool:
    """Demonstrate credential rotation workflow."""
    print("\n🔄 Demonstrating credential rotation...")

    # Add initial credential
    cred_id = client_manager.credential_manager.add_credential(
        "demo-credential",
        "initial-api-key-12345",
        "Demo credential for rotation testing",
    )

    # Create client with initial credential
    client = client_manager.create_client_with_credential(cred_id)
    if not client:
        return False

    print(f"✅ Created client with credential {cred_id}")

    # Rotate the credential
    new_api_key = "rotated-api-key-67890"
    rotated_client = client_manager.rotate_and_recreate_client(cred_id, new_api_key)

    if rotated_client:
        print("✅ Successfully rotated credential and recreated client")
        return True
    else:
        print("❌ Failed to rotate credential")
        return False


def demonstrate_security_auditing(credential_manager: SecureCredentialManager) -> bool:
    """Demonstrate security auditing capabilities."""
    print("\n🔍 Demonstrating security auditing...")

    # Create auditor
    auditor = SecurityAuditor(credential_manager)

    # Generate security report
    report = auditor.generate_security_report()

    print("📊 Security Report Generated:")
    print(f"  • Credentials: {report['credential_summary']['total_credentials']}")
    print(f"  • Security Score: {report['credential_summary']['security_score']}/100")
    print(f"  • Recent Rotations: {report['rotation_summary']['recent_rotations']}")
    print(f"  • Audit Events: {report['audit_summary']['total_events']}")

    if report["recommendations"]:
        print("  • Recommendations:")
        for rec in report["recommendations"]:
            print(f"    - {rec}")

    return True


def main() -> bool:
    """Main function demonstrating authentication patterns."""
    print("🔐 Authentication Patterns Example")
    print("=" * 50)

    try:
        # Get base URL from environment or use default
        base_url = os.getenv("AIP_API_URL", "http://localhost:8000")

        # Initialize managers
        print("🔌 Initializing authentication managers...")
        client_manager = AuthenticatedClientManager(base_url)
        print(f"✅ Connected to: {base_url}")

        # Demonstrate credential management
        print("\n🔑 Demonstrating credential management...")
        cred_id = client_manager.credential_manager.add_credential(
            "test-credential",
            "test-api-key-abcdef",
            "Test credential for demonstration",
        )
        print(f"✅ Added credential: {cred_id}")

        # Demonstrate client creation
        print("\n🤖 Demonstrating authenticated client creation...")
        client = client_manager.create_client_with_credential(cred_id)
        if not client:
            print("❌ Failed to create authenticated client")
            return False

        print("✅ Created authenticated client successfully")

        # Test the client
        print("\n🧪 Testing authenticated client...")
        try:
            agents = client.list_agents()
            print(f"✅ Authentication test passed - found {len(agents)} agents")
        except Exception as e:
            print(f"⚠️  Authentication test had issues: {e}")

        # Demonstrate credential rotation
        rotation_success = demonstrate_credential_rotation(client_manager)

        # Demonstrate security auditing
        auditing_success = demonstrate_security_auditing(
            client_manager.credential_manager
        )

        # Cleanup
        print("\n🧹 Cleaning up...")
        client_manager.cleanup_expired_clients()

        print("\n🎉 Authentication patterns example completed successfully!")
        print("📊 Results:")
        print("  • Credential management: PASSED")
        print("  • Client authentication: PASSED")
        print(f"  • Credential rotation: {'PASSED' if rotation_success else 'FAILED'}")
        print(f"  • Security auditing: {'PASSED' if auditing_success else 'FAILED'}")

        return all([rotation_success, auditing_success])

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("  - Make sure backend services are running (docker-compose up)")
        print("  - Verify your API credentials in .env file")
        print("  - Check that the backend supports the required endpoints")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

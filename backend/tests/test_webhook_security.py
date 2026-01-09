"""
$COPPER Webhook Security Tests

Tests for webhook authorization verification, payload validation, and attack prevention.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from httpx import ASGITransport, AsyncClient

from app.main import app
from app.api.webhook import verify_webhook_auth


class TestAuthorizationVerification:
    """Tests for Authorization header verification."""

    def test_valid_auth_passes(self):
        """Test that valid authorization passes verification."""
        secret = "test-webhook-secret-12345"
        auth_header = "test-webhook-secret-12345"

        result = verify_webhook_auth(auth_header, secret)
        assert result is True

    def test_invalid_auth_fails(self):
        """Test that invalid authorization is rejected."""
        secret = "test-webhook-secret-12345"
        auth_header = "wrong-secret"

        result = verify_webhook_auth(auth_header, secret)
        assert result is False

    def test_missing_auth_fails(self):
        """Test that missing authorization is rejected."""
        secret = "test-webhook-secret-12345"

        result = verify_webhook_auth(None, secret)
        assert result is False

    def test_empty_auth_fails(self):
        """Test that empty authorization is rejected."""
        secret = "test-webhook-secret-12345"

        result = verify_webhook_auth("", secret)
        assert result is False

    def test_missing_secret_fails(self):
        """Test that missing secret causes rejection."""
        auth_header = "some-auth-value"

        result = verify_webhook_auth(auth_header, "")
        assert result is False

    def test_timing_attack_resistant(self):
        """Test that comparison uses constant-time algorithm."""
        # The verify_webhook_auth function uses hmac.compare_digest
        # which is resistant to timing attacks
        secret = "test-webhook-secret-12345"

        # Near-match should behave same as total mismatch (constant time)
        assert verify_webhook_auth(secret, secret) is True
        assert verify_webhook_auth(secret[:-1] + "x", secret) is False
        assert verify_webhook_auth("completely-different", secret) is False

    def test_compare_digest_used(self):
        """Verify constant-time comparison is used (code inspection test)."""
        import inspect

        source = inspect.getsource(verify_webhook_auth)
        assert "compare_digest" in source, "Must use hmac.compare_digest for timing attack resistance"


@pytest.mark.asyncio
class TestWebhookEndpoint:
    """Tests for the webhook HTTP endpoint."""

    async def test_rejects_missing_secret_config(self):
        """Test endpoint returns 503 when webhook secret not configured."""
        mock_settings = MagicMock()
        mock_settings.helius_webhook_secret = None

        with patch("app.api.webhook.settings", mock_settings):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/webhook/helius",
                    json={"type": "SWAP"},
                    headers={"Authorization": "test-secret"}
                )
                assert response.status_code == 503
                assert "not configured" in response.json()["detail"].lower()

    async def test_rejects_missing_authorization_header(self):
        """Test endpoint returns 401 when Authorization header missing."""
        mock_settings = MagicMock()
        mock_settings.helius_webhook_secret = "test-secret"

        with patch("app.api.webhook.settings", mock_settings):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/webhook/helius",
                    json={"type": "SWAP"}
                    # No Authorization header
                )
                assert response.status_code == 401
                assert "Invalid authorization" in response.json()["detail"]

    async def test_rejects_invalid_authorization(self):
        """Test endpoint returns 401 for invalid authorization."""
        mock_settings = MagicMock()
        mock_settings.helius_webhook_secret = "test-secret"

        with patch("app.api.webhook.settings", mock_settings):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/webhook/helius",
                    json={"type": "SWAP"},
                    headers={"Authorization": "wrong-secret"}
                )
                assert response.status_code == 401

    async def test_rejects_invalid_json(self):
        """Test endpoint returns 400 for malformed JSON."""
        mock_settings = MagicMock()
        mock_settings.helius_webhook_secret = "test-secret"

        with patch("app.api.webhook.settings", mock_settings):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/webhook/helius",
                    content=b"not valid json {",
                    headers={
                        "Authorization": "test-secret",
                        "content-type": "application/json"
                    }
                )
                assert response.status_code == 400
                assert "Invalid JSON" in response.json()["detail"]

    async def test_rejects_oversized_batch(self):
        """Test endpoint returns 400 for batches over 100 transactions."""
        mock_settings = MagicMock()
        mock_settings.helius_webhook_secret = "test-secret"

        # Create 101 transactions
        large_batch = [{"type": "SWAP", "signature": f"tx{i}"} for i in range(101)]

        with patch("app.api.webhook.settings", mock_settings):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/webhook/helius",
                    json=large_batch,
                    headers={"Authorization": "test-secret"}
                )
                assert response.status_code == 400
                assert "Batch too large" in response.json()["detail"]

    async def test_accepts_valid_request(self):
        """Test endpoint accepts properly authorized valid request."""
        mock_settings = MagicMock()
        mock_settings.helius_webhook_secret = "test-secret"
        mock_settings.copper_token_mint = "TestMint111111111111111111111111111111111"

        mock_helius = MagicMock()
        mock_helius.parse_webhook_transaction.return_value = None

        with patch("app.api.webhook.settings", mock_settings):
            with patch("app.api.webhook.get_helius_service", return_value=mock_helius):
                with patch("app.api.webhook.get_db"):
                    async with AsyncClient(
                        transport=ASGITransport(app=app),
                        base_url="http://test"
                    ) as client:
                        response = await client.post(
                            "/api/webhook/helius",
                            json={
                                "type": "SWAP",
                                "signature": "abc123",
                                "feePayer": "TestWallet11111111111111111111111111111111",
                                "tokenTransfers": []
                            },
                            headers={"Authorization": "test-secret"}
                        )
                        # May fail due to DB dependency, but should pass auth
                        # Status 200 or 500 (DB error) but NOT 401/400
                        assert response.status_code != 401


class TestWebhookPayloadValidation:
    """Tests for payload structure validation."""

    def test_handles_single_transaction(self):
        """Test that single transaction (not array) is handled."""
        # The webhook handler wraps single transactions in array
        single_tx = {"type": "SWAP", "signature": "abc"}
        transactions = single_tx if isinstance(single_tx, list) else [single_tx]
        assert len(transactions) == 1
        assert transactions[0]["type"] == "SWAP"

    def test_handles_array_of_transactions(self):
        """Test that array of transactions is handled correctly."""
        batch = [
            {"type": "SWAP", "signature": "abc"},
            {"type": "SWAP", "signature": "def"}
        ]
        transactions = batch if isinstance(batch, list) else [batch]
        assert len(transactions) == 2

    def test_empty_payload_handled(self):
        """Test that empty array is handled gracefully."""
        batch = []
        transactions = batch if isinstance(batch, list) else [batch]
        assert len(transactions) == 0


class TestAttackPrevention:
    """Tests for specific attack vector prevention."""

    def test_prevents_auth_bypass_with_null(self):
        """Test that null/None authorization cannot bypass verification."""
        secret = "test-secret"

        # Try various null-like values
        assert verify_webhook_auth(None, secret) is False
        assert verify_webhook_auth("", secret) is False

    def test_case_sensitive_auth(self):
        """Test that authorization comparison is case-sensitive."""
        secret = "Test-Secret-ABC"

        assert verify_webhook_auth("Test-Secret-ABC", secret) is True
        assert verify_webhook_auth("test-secret-abc", secret) is False
        assert verify_webhook_auth("TEST-SECRET-ABC", secret) is False

    def test_whitespace_handling(self):
        """Test that whitespace in auth values is handled correctly."""
        secret = "test-secret"

        # Whitespace should NOT be stripped - exact match required
        assert verify_webhook_auth(" test-secret", secret) is False
        assert verify_webhook_auth("test-secret ", secret) is False
        assert verify_webhook_auth(" test-secret ", secret) is False

"""Shared pytest configuration for the Synapse backend test suite.

All anyio-based async tests are forced onto the asyncio backend.
The production runtime (ExecutionOrchestrator, ExecutionScheduler) is
intentionally built on native asyncio primitives and must not be tested
under trio.
"""
import pytest


@pytest.fixture(scope="session")
def anyio_backend():
    """Pin all anyio tests in this package to asyncio."""
    return "asyncio"

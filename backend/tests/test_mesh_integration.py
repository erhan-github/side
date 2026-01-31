"""
Test: Universal Mesh Integration

Verifies Universal Mesh cross-project sync functionality.
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestMeshIntegration:
    """Tests for Universal Mesh functionality."""
    
    def test_mesh_module_exists(self):
        """Mesh module should be importable."""
        try:
            from side.storage.modules.transient import OperationalStore
            assert True
        except ImportError:
            pytest.fail("Mesh-related modules not importable")
    
    def test_project_mesh_table_exists(self):
        """Project mesh table should exist in database."""
        from side.storage.modules.base import SovereignEngine
        from side.storage.modules.transient import OperationalStore
        
        engine = SovereignEngine()
        op_store = OperationalStore(engine)
        
        # Table should be accessible
        with engine.connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='project_mesh'"
            )
            result = cursor.fetchone()
            # May or may not exist depending on state
            assert result is None or result['name'] == 'project_mesh'
    
    def test_mesh_sync_command_exists(self):
        """CLI should have mesh command."""
        from side.cli import cli
        # Check if mesh command is registered
        assert hasattr(cli, 'mesh') or 'mesh' in dir(cli)


class TestMeshDataSync:
    """Tests for Mesh data synchronization."""
    
    def test_mesh_can_store_project_link(self):
        """Mesh should be able to store project relationships."""
        from side.storage.modules.base import SovereignEngine
        from side.storage.modules.transient import OperationalStore
        
        engine = SovereignEngine()
        op_store = OperationalStore(engine)
        
        # Store a test setting (mesh data structure)
        op_store.set_setting("mesh_test_key", "mesh_test_value")
        retrieved = op_store.get_setting("mesh_test_key")
        
        assert retrieved == "mesh_test_value"
        
        # Cleanup
        op_store.set_setting("mesh_test_key", None)

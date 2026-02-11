from side.protocols.cli import CLIProtocol

# Global UI Instance
ux = CLIProtocol()

# Storage Factories
def get_engine():
    from side.storage.modules.base import ContextEngine
    return ContextEngine()

def get_user_profile(engine):
    from side.storage.modules.identity import IdentityService
    return IdentityService(engine)

def get_project_plan(engine):
    from side.storage.modules.strategy import StrategicStore
    return StrategicStore(engine)

def get_audit_log(engine):
    from side.storage.modules.audit import AuditService
    return AuditService(engine)

def get_transient(engine):
    from side.storage.modules.transient import SessionCache
    return SessionCache(engine)

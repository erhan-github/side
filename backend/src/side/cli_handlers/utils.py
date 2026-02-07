from side.protocols.cli import CLIProtocol

# Global UI Instance
ux = CLIProtocol()

# Storage Factories
def get_engine():
    from side.storage.modules.base import ContextEngine
    return ContextEngine()

def get_identity(engine):
    from side.storage.modules.identity import IdentityStore
    return IdentityStore(engine)

def get_strategic(engine):
    from side.storage.modules.chronos import ChronosStore
    return ChronosStore(engine)

def get_audit(engine):
    from side.storage.modules.audit import AuditStore
    return AuditStore(engine)

def get_transient(engine):
    from side.storage.modules.transient import OperationalStore
    return OperationalStore(engine)

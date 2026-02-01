# SOVEREIGN ANCHOR: 8e787d673427795a
> **Generated:** 2026-02-01T08:38:15.492783+00:00
> **Purpose:** LLM Boot Disk (Forensic Reality)
> **Verification:** SHA-256 Merkle Proof & Live Schema

## 1. OPERATIONAL REALITY (The Truth)
*Source: Git Forensic Log (Objective)*
**Recent Commits (The Vector):**
- 0cfc7f9 feat: God Mode Visual & Karpathy Narrative (2 hours ago)
- ae25dc4 feat(core): Stockholm Summit Release (Code Only) - docs redacted (26 hours ago)
- 18de81f feat(pricing): implement Groq MVP strategy with Gemini migration path (2 days ago)
- a06720f feat(pricing): implement premium Claude 4.5 pricing strategy (2 days ago)
- 89490a7 feat(pricing): implement dynamic SU calculation engine (2 days ago)

**Active Measures (The Now):**
- D backend/src/side/intel/adaptive_context_engine.py
-  M backend/src/side/intel/auto_intelligence.py
-  D backend/src/side/intel/context_allocator.py
-  M backend/src/side/intel/conversation_session.py
-  M backend/src/side/intel/ecosystem/jetbrains.py
-  D backend/src/side/intel/intent_context_injector.py
-  D backend/src/side/intel/relevance_engine.py
-  D backend/src/side/intel/verification_director.py
-  M backend/src/side/pulse.py
-  M backend/src/side/qa/generator.py


## 2. DATA SOVEREIGNTY (The Law)
*Source: Live Codebase (Verified)*
```python
# --- INTENT (Pydantic V2) ---
{
  "$defs": {
    "ClaimedOutcome": {
      "enum": [
        "FIXED",
        "ONGOING",
        "ABANDONED",
        "UNKNOWN"
      ],
      "title": "ClaimedOutcome",
      "type": "string"
    },
    "IntentCategory": {
      "enum": [
        "DEBUGGING",
        "IMPLEMENTING",
        "RESEARCHING",
        "REFACTORING",
        "CONFIGURING",
        "UNKNOWN"
      ],
      "title": "IntentCategory",
      "type": "string"
    },
    "VerifiedOutcome": {
      "enum": [
        "CONFIRMED",
        "FALSE_POSITIVE",
        "UNVERIFIABLE",
        "NOT_APPLICABLE"
      ],
      "title": "VerifiedOutcome",
      "type": "string"
    }
  },
  "description": "A single LLM-User exchange session from Antigravity.",
  "properties": {
    "session_id": {
      "title": "Session Id",
      "type": "string"
    },
    "project_id": {
      "default": "",
      "title": "Project Id",
      "type": "string"
    },
    "started_at": {
      "format": "date-time",
      "title": "Started At",
      "type": "string"
    },
    "ended_at": {
      "anyOf": [
        {
          "format": "date-time",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Ended At"
    },
    "duration_seconds": {
      "default": 0.0,
      "title": "Duration Seconds",
      "type": "number"
    },
    "raw_intent": {
      "default": "",
      "title": "Raw Intent",
      "type": "string"
    },
    "intent_vector": {
      "items": {
        "type": "string"
      },
      "title": "Intent Vector",
      "type": "array"
    },
    "intent_category": {
      "$ref": "#/$defs/IntentCategory",
      "default": "UNKNOWN"
    },
    "claimed_outcome": {
      "$ref": "#/$defs/ClaimedOutcome",
      "default": "UNKNOWN"
    },
    "verified_outcome": {
      "anyOf": [
        {
          "$ref": "#/$defs/VerifiedOutcome"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "prior_sessions": {
      "items": {
        "type": "string"
      },
      "title": "Prior Sessions",
      "type": "array"
    },
    "follow_up_sessions": {
      "items": {
        "type": "string"
      },
      "title": "Follow Up Sessions",
      "type": "array"
    }
  },
  "title": "ConversationSession",
  "type": "object"
}

# --- PHYSICS (Pydantic V2) ---
{
  "$defs": {
    "PulseStatus": {
      "enum": [
        "SECURE",
        "DRIFT",
        "VIOLATION"
      ],
      "title": "PulseStatus",
      "type": "string"
    }
  },
  "description": "The outcome of a Sovereign Pulse Check.",
  "properties": {
    "status": {
      "$ref": "#/$defs/PulseStatus"
    },
    "latency_ms": {
      "title": "Latency Ms",
      "type": "number"
    },
    "violations": {
      "items": {
        "type": "string"
      },
      "title": "Violations",
      "type": "array"
    },
    "context": {
      "additionalProperties": true,
      "title": "Context",
      "type": "object"
    }
  },
  "required": [
    "status",
    "latency_ms"
  ],
  "title": "PulseResult",
  "type": "object"
}

# --- LEDGER (Pydantic V2) ---
{
  "$defs": {
    "LedgerEntryType": {
      "enum": [
        "ACTIVITY",
        "AUDIT",
        "WORK_CONTEXT",
        "OUTCOME"
      ],
      "title": "LedgerEntryType",
      "type": "string"
    }
  },
  "description": "A unified entry in the Sovereign Ledger.",
  "properties": {
    "id": {
      "title": "Id",
      "type": "string"
    },
    "project_id": {
      "title": "Project Id",
      "type": "string"
    },
    "entry_type": {
      "$ref": "#/$defs/LedgerEntryType"
    },
    "tool": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Tool"
    },
    "action": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Action"
    },
    "severity": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Severity"
    },
    "cost_tokens": {
      "default": 0,
      "title": "Cost Tokens",
      "type": "integer"
    },
    "tier": {
      "default": "free",
      "title": "Tier",
      "type": "string"
    },
    "payload": {
      "additionalProperties": true,
      "title": "Payload",
      "type": "object"
    },
    "message": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Message"
    },
    "created_at": {
      "format": "date-time",
      "title": "Created At",
      "type": "string"
    }
  },
  "required": [
    "project_id",
    "entry_type"
  ],
  "title": "LedgerEntry",
  "type": "object"
}

# --- BRAIN (Pydantic V2) ---
{
  "$defs": {
    "BrainStats": {
      "properties": {
        "nodes": {
          "title": "Nodes",
          "type": "integer"
        },
        "total_size_bytes": {
          "default": 0,
          "title": "Total Size Bytes",
          "type": "integer"
        },
        "total_lines": {
          "default": 0,
          "title": "Total Lines",
          "type": "integer"
        },
        "mode": {
          "default": "Distributed",
          "title": "Mode",
          "type": "string"
        }
      },
      "required": [
        "nodes"
      ],
      "title": "BrainStats",
      "type": "object"
    },
    "DNA": {
      "properties": {
        "detected_stack": {
          "items": {
            "type": "string"
          },
          "title": "Detected Stack",
          "type": "array"
        },
        "primary_languages": {
          "items": {
            "type": "string"
          },
          "title": "Primary Languages",
          "type": "array"
        },
        "signals": {
          "items": {
            "type": "string"
          },
          "title": "Signals",
          "type": "array"
        }
      },
      "title": "DNA",
      "type": "object"
    },
    "FractalNode": {
      "description": "A single file or directory in the Fractal Index.",
      "properties": {
        "path": {
          "title": "Path",
          "type": "string"
        },
        "type": {
          "title": "Type",
          "type": "string"
        },
        "name": {
          "title": "Name",
          "type": "string"
        },
        "size": {
          "title": "Size",
          "type": "integer"
        },
        "lines": {
          "title": "Lines",
          "type": "integer"
        },
        "digest": {
          "title": "Digest",
          "type": "string"
        },
        "semantics": {
          "anyOf": [
            {
              "$ref": "#/$defs/FractalSemantics"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        }
      },
      "required": [
        "path",
        "type",
        "name",
        "size",
        "lines",
        "digest"
      ],
      "title": "FractalNode",
      "type": "object"
    },
    "FractalSemantics": {
      "properties": {
        "classes": {
          "items": {
            "type": "string"
          },
          "title": "Classes",
          "type": "array"
        },
        "functions": {
          "items": {
            "type": "string"
          },
          "title": "Functions",
          "type": "array"
        },
        "signals": {
          "items": {
            "type": "string"
          },
          "title": "Signals",
          "type": "array"
        }
      },
      "title": "FractalSemantics",
      "type": "object"
    }
  },
  "description": "The Indexed Brain of a Sidelith-managed Project.\nReplaces `sovereign.schema.json`.",
  "properties": {
    "version": {
      "default": "3.1.0",
      "title": "Version",
      "type": "string"
    },
    "last_scan": {
      "format": "date-time",
      "title": "Last Scan",
      "type": "string"
    },
    "dna": {
      "$ref": "#/$defs/DNA"
    },
    "stats": {
      "$ref": "#/$defs/BrainStats"
    },
    "nodes": {
      "items": {
        "$ref": "#/$defs/FractalNode"
      },
      "title": "Nodes",
      "type": "array"
    },
    "history_fragments": {
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "title": "History Fragments",
      "type": "array"
    },
    "strategic_timeline": {
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "title": "Strategic Timeline",
      "type": "array"
    }
  },
  "required": [
    "stats"
  ],
  "title": "SovereignGraph",
  "type": "object"
}
```

## 3. FRACTAL REALITY (The Map)
*Merkle Tree Snapshot*
```text
. [8e787d673427795a]
├── .gitignore [1b7ed634]
├── README.md [760d2c04]
├── SOVEREIGN_ANCHOR.md [9dc8e63a]
├── requirements.txt [d6b677b9]
├── verify_phoenix.py [ac6904e0]
├── .github/ [Merkle: c75de2ef]
├── backend/ [Merkle: 918b753f]
│   ├── .gitignore [45bf4062]
│   ├── Dockerfile [b6ed09ef]
│   ├── LICENSE [cd5ec895]
│   ├── README.md [822f5e4d]
│   ├── TROUBLESHOOTING.md [50719e9f]
│   ├── benchmark_mmap.py [20db9eaa]
│   ├── benchmark_pulse.py [fb29b6cd]
│   ├── pyproject.toml [c74d7e69]
│   ├── railway.toml [03ef51c1]
│   ├── requirements.txt [e01ed614]
│   ├── .pytest_cache/ [Merkle: 36eb08e1]
│   │   ├── .gitignore [3ed731b6]
│   │   ├── CACHEDIR.TAG [37dc88ef]
│   │   ├── README.md [73fd6fcc]
│   │   └── v/ [Merkle: c75de2ef]
│   ├── src/ [Merkle: 7b406e15]
│   │   ├── cli_import_profile.txt [1eea5140]
│   │   ├── import_profile.txt [027d2660]
│   │   ├── verify_context_graph.py [55f968d9]
│   │   └── side/ [Merkle: 5628d81b]
│   │       ├── __init__.py [5ef0b5c5]
│   │       ├── cli.py [174abe56]
│   │       ├── config.py [5eaba7b2]
│   │       ├── env.py [f124e571]
│   │       ├── logging_config.py [a37fea5a]
│   │       ├── onboarding.py [45a95a48]
│   │       ├── prompts.py [01d01efb]
│   │       ├── pulse.py [ae813507]
│   │       ├── resources.py [f4e635f4]
│   │       ├── server.py [d9a26a34]
│   │       ├── tools_handler.py [bf29f73a]
│   │       ├── verify_task_engine.py [d4f9c22c]
│   │       ├── watcher_daemon.py [b0596d36]
│   │       ├── auth/ [Merkle: 55165900]
│   │       │   ├── __init__.py [81401f95]
│   │       │   ├── fastapi_deps.py [3efe04fb]
│   │       │   ├── github.py [a796fd27]
│   │       │   ├── supabase_auth.py [9f39b48d]
│   │       │   └── users.py [dccfb313]
│   │       ├── backend/ [Merkle: 8749726d]
│   │       │   └── src/ [Merkle: c91c19da]
│   │       │       └── side/ [Merkle: c75de2ef]
│   │       ├── common/ [Merkle: 863ca7e0]
│   │       │   └── notifications.py [5ff0eba2]
│   │       ├── instrumentation/ [Merkle: 1e3d3430]
│   │       │   ├── __init__.py [e3b0c442]
│   │       │   └── engine.py [381b55e8]
│   │       ├── intel/ [Merkle: 0675a737]
│   │       │   ├── __init__.py [e3b0c442]
│   │       │   ├── adaptive_context_engine.py [d6835ac9]
│   │       │   ├── auto_intelligence.py [a984ce94]
│   │       │   ├── bridge.py [832a62b1]
│   │       │   ├── cloud_distiller.py [f4fc482f]
│   │       │   ├── context_allocator.py [eb945497]
│   │       │   ├── conversation_ingester.py [7e062001]
│   │       │   ├── conversation_session.py [fc341d86]
│   │       │   ├── drill_compliance.py [72e3dbc7]
│   │       │   ├── drill_cursor.py [59331811]
│   │       │   ├── drill_ecosystem.py [d937e293]
│   │       │   ├── drill_full_summit.py [c0470772]
│   │       │   ├── drill_intent.py [97a0fe59]
│   │       │   ├── drill_phase_2.py [23b12d55]
│   │       │   ├── drill_phase_3.py [623ee356]
│   │       │   ├── drill_scavenger.py [1fdbfcf0]
│   │       │   ├── drill_summit.py [d76bad84]
│   │       │   ├── episodic_projector.py [65bb6ba9]
│   │       │   ├── forensic_allowlist.py [0bb93680]
│   │       │   ├── fractal_indexer.py [f34cd0fa]
│   │       │   ├── generate_report.py [ac562ede]
│   │       │   ├── hardware.py [49391c1a]
│   │       │   ├── intent_analyzer.py [dd8bd1f6]
│   │       │   ├── intent_context_injector.py [ff36697c]
│   │       │   ├── isolation_audit.py [920b32fb]
│   │       │   ├── language_detector.py [bd869a79]
│   │       │   ├── log_scavenger.py [d0662061]
│   │       │   ├── memory.py [a1ea42e6]
│   │       │   ├── metrics_calculator.py [ad1a1fb2]
│   │       │   ├── outcome_verifier.py [d3376fea]
│   │       │   ├── reasoning.py [f50074f0]
│   │       │   ├── reasoning_timeline.py [d401d8ed]
│   │       │   ├── relevance_engine.py [cac620f6]
│   │       │   ├── semantic_auditor.py [8f77e2da]
│   │       │   ├── sensor.py [128985f6]
│   │       │   ├── synergy.py [404c7d5e]
│   │       │   ├── telemetry.py [50c33d05]
│   │       │   ├── trainer.py [5f99a991]
│   │       │   ├── types.py [021c63f4]
│   │       │   ├── verification_director.py [56aee124]
│   │       │   ├── watcher.py [d53a9521]
│   │       │   ├── ecosystem/ [Merkle: 5c05098d]
│   │       │   │   └── jetbrains.py [415a6c25]
│   │       │   ├── safety/ [Merkle: b0a9ca85]
│   │       │   │   └── drift_detector.py [e8c2d94e]
│   │       │   ├── scavengers/ [Merkle: 2f53f22b]
│   │       │   │   ├── docker.py [6c8f4e26]
│   │       │   │   └── mobile.py [38de2553]
│   │       │   └── sources/ [Merkle: cd73c5e0]
│   │       │       ├── antigravity.py [3d455717]
│   │       │       ├── base.py [833ec072]
│   │       │       ├── cursor.py [dfd27c60]
│   │       │       └── jira_linear.py [fce1fa0e]
│   │       ├── llm/ [Merkle: 4dd8d040]
│   │       │   ├── __init__.py [0e537c32]
│   │       │   ├── client.py [d9ac0054]
│   │       │   ├── factory.py [69bb6251]
│   │       │   ├── managed_pool.py [05e77a7f]
│   │       │   ├── model_router.py [d568ea1b]
│   │       │   ├── orchestrator.py [40678380]
│   │       │   └── prompts.py [8f0d8de5]
│   │       ├── mesh/ [Merkle: d380fc26]
│   │       │   ├── __init__.py [3d6c8dc0]
│   │       │   ├── api.py [660d49c3]
│   │       │   ├── auth.py [49f24e09]
│   │       │   ├── limiter.py [6f6b5327]
│   │       │   └── s3_protocol.py [1e9507ae]
│   │       ├── parallel/ [Merkle: 6e6bc4bb]
│   │       │   ├── __init__.py [6ed3b7ce]
│   │       │   └── task_decomposer.py [63e0313b]
│   │       ├── proof/ [Merkle: 7f0c2331]
│   │       │   └── neural_heartbeat.py [3582c173]
│   │       ├── qa/ [Merkle: 45531403]
│   │       │   └── generator.py [5dd44142]
│   │       ├── security/ [Merkle: 22e33b61]
│   │       │   ├── __init__.py [edb9ce83]
│   │       │   ├── keychain.py [3ac8480b]
│   │       │   └── sqlcipher.py [53e0551c]
│   │       ├── services/ [Merkle: e31ac657]
│   │       │   ├── __init__.py [5d6209d1]
│   │       │   ├── billing.py [c066b00f]
│   │       │   ├── causal_ledger.py [82a0b2f6]
│   │       │   ├── cleanup_scheduler.py [b15d0fc0]
│   │       │   ├── context_tracker.py [cb177c6c]
│   │       │   ├── file_watcher.py [e45a15e0]
│   │       │   ├── hub.py [b65c9f4f]
│   │       │   ├── ignore.py [6ca7851c]
│   │       │   ├── integrity.py [8b40f798]
│   │       │   ├── polyglot_proxy.py [55513e97]
│   │       │   ├── proactive_service.py [19e321fb]
│   │       │   ├── qa_service.py [71cdfa63]
│   │       │   ├── roi_simulator.py [48ef22c7]
│   │       │   ├── rolling_chronicle.py [8e7fe0b2]
│   │       │   ├── service_manager.py [5ad92819]
│   │       │   ├── shadow_intent.py [fbe7198c]
│   │       │   ├── signal_auditor.py [ec6b65e6]
│   │       │   ├── silicon_pulse.py [99f0d881]
│   │       │   ├── socket_listener.py [721baa21]
│   │       │   ├── strategic_scavenger.py [bdc77057]
│   │       │   ├── temporal_auditor.py [c70d2114]
│   │       │   ├── unified_buffer.py [bc55fcbd]
│   │       │   └── watcher_service.py [f463e9db]
│   │       ├── storage/ [Merkle: 05964ab4]
│   │       │   ├── __init__.py [1de0aaaf]
│   │       │   ├── database.py [e60fe373]
│   │       │   ├── portability.py [fd839253]
│   │       │   ├── simple_db.py [1d4ef299]
│   │       │   └── modules/ [Merkle: d993edca]
│   │       │       ├── accounting.py [baa8eed6]
│   │       │       ├── base.py [7ee2db27]
│   │       │       ├── forensic.py [24fa97d3]
│   │       │       ├── identity.py [208f02d6]
│   │       │       ├── intent_fusion.py [b9b4cce9]
│   │       │       ├── mmap_store.py [7d8f82a7]
│   │       │       ├── strategic.py [7530c117]
│   │       │       └── transient.py [84afcc0d]
│   │       ├── terminal/ [Merkle: 77ed7f12]
│   │       │   └── monitor.py [79774a72]
│   │       ├── tools/ [Merkle: 585d3030]
│   │       │   ├── __init__.py [e95d7f1f]
│   │       │   ├── audit.py [45cb543a]
│   │       │   ├── core.py [33cad2b9]
│   │       │   ├── definitions.py [f1938730]
│   │       │   ├── forensics_tool.py [045cad16]
│   │       │   ├── formatting.py [2f6de065]
│   │       │   ├── get_spc.py [d108f993]
│   │       │   ├── micro_audit.py [8c35c02a]
│   │       │   ├── planning.py [f281af15]
│   │       │   ├── recursive_utils.py [374b343c]
│   │       │   ├── router.py [fa4cefa4]
│   │       │   ├── strategy.py [7cb338ed]
│   │       │   ├── verification.py [5b2713c7]
│   │       │   ├── welcome.py [8e87c33d]
│   │       │   ├── worktree_manager.py [f60c63de]
│   │       │   └── forensics/ [Merkle: 0382e6a7]
│   │       │       ├── __init__.py [30ec4f25]
│   │       │       ├── bandit.py [23007096]
│   │       │       ├── base.py [42502150]
│   │       │       ├── detekt.py [7aab5e7a]
│   │       │       ├── eslint.py [19330987]
│   │       │       ├── gosec.py [1eb66d3b]
│   │       │       ├── semgrep.py [a310b9fa]
│   │       │       ├── swiftlint.py [7716e751]
│   │       │       └── synthesizer.py [62d3b906]
│   │       └── utils/ [Merkle: 3bf5e289]
│   │           ├── __init__.py [349b9b7d]
│   │           ├── crypto.py [3518e290]
│   │           ├── errors.py [b20da826]
│   │           ├── fast_ast.py [6d75d6cc]
│   │           ├── hashing.py [8cc8fd22]
│   │           ├── helpers.py [c2728540]
│   │           ├── labels.py [f917f885]
│   │           ├── paths.py [7a85e226]
│   │           ├── performance.py [4a02abfb]
│   │           ├── retry.py [19b0f8ad]
│   │           ├── security.py [1320fcc1]
│   │           ├── shield.py [af651db4]
│   │           └── soul.py [8ec82130]
│   ├── supabase/ [Merkle: d199dcb3]
│   │   ├── schema.sql [f9b47c91]
│   │   └── migrations/ [Merkle: 4fff2dea]
│   │       ├── 002_tenant_isolation.sql [d34d3c63]
│   │       ├── 003_wallet_ledger.sql [85591666]
│   │       ├── 003_wallet_ledger_fix.sql [16728ce1]
│   │       ├── 004_billing_fields.sql [031db1eb]
│   │       ├── 005_fix_profile_perms.sql [f464e3ae]
│   │       └── 20260122_findings_and_activities.sql [ea8ac92e]
│   ├── templates/ [Merkle: 47e9b9d7]
│   │   └── audits/ [Merkle: dae91922]
│   │       └── pre_launch_v1.md [436c24f9]
│   └── tests/ [Merkle: c407a8d6]
│       ├── __init__.py [ee81d2e4]
│       ├── load_test_projects.py [38ca2924]
│       ├── load_test_rls.py [35f1e758]
│       ├── stress_test_e2e.py [36fad360]
│       ├── test_auto_intelligence.py [2fae1aef]
│       ├── test_circuit_breaker.py [71e65169]
│       ├── test_errors.py [0e2475bf]
│       ├── test_mesh_integration.py [c2a479e1]
│       ├── test_mmap_performance.py [006ab6c7]
│       ├── test_ollama_airgap.py [4e2f5fb2]
│       ├── test_phoenix_recovery.py [e6fcd3ee]
│       ├── test_polyglot.rs [825de36c]
│       ├── test_polyglot.ts [a3c903f4]
│       ├── test_pulse_latency.py [672df89e]
│       ├── test_query_cache.py [e5585905]
│       ├── test_simple_db.py [8a51a700]
│       ├── test_strategic_engine.py [f5bbd755]
│       ├── test_task_decomposer.py [cd74076a]
│       ├── test_technical.py [53725083]
│       ├── forensic_audit/ [Merkle: 5216e3f8]
│       │   └── test_probes.py [d1a26679]
│       ├── hostile/ [Merkle: 9eeac85b]
│       │   ├── test_hostile_clean_root.py [24a3d916]
│       │   ├── test_hostile_tail_file.py [ce8c9100]
│       │   └── test_hostile_verify_scaler.py [14a2d41d]
│       └── red_team/ [Merkle: 755edeed]
│           ├── test_firewall_leak.py [49599fa2]
│           ├── test_full_sovereign_cycle.py [b9e5a939]
│           ├── test_latency_storm.py [64277be9]
│           └── test_neural_uplink.py [eff93fc6]
├── cli/ [Merkle: b5c6e1f9]
│   ├── index.js [4ec0a90f]
│   └── package.json [e47e73e8]
├── mcp-package/ [Merkle: e9ae3a89]
│   ├── README.md [9ded8321]
│   └── package.json [50ae850a]
├── tests/ [Merkle: 78c23653]
│   └── verify_full_loop.py [c9289089]
└── web/ [Merkle: ce6cb187]
    ├── .dockerignore [f74abd9e]
    ├── .gitignore [207e265f]
    ├── .npmrc [a093bb2f]
    ├── .nvmrc [53787963]
    ├── Dockerfile [cf36be68]
    ├── README.md [60b55ff7]
    ├── components.json [69e0b1e4]
    ├── eslint.config.mjs [870f1adc]
    ├── middleware.ts [671cda89]
    ├── next-env.d.ts [7ad303e4]
    ├── next.config.ts [dff23832]
    ├── package-lock.json [8cfbaf0e]
    ├── package.json [2381f033]
    ├── postcss.config.mjs [dfac7ac2]
    ├── railway.toml [fa55b9cb]
    ├── sentry.client.config.ts [7bc69147]
    ├── sentry.server.config.ts [e2674813]
    ├── supabase_spec.json [7aaa1e07]
    ├── tsconfig.json [4e56b93d]
    ├── app/ [Merkle: c17b2446]
    │   ├── error.tsx [71cfa424]
    │   ├── favicon.ico [f72ca688]
    │   ├── globals.css [b377a986]
    │   ├── layout.tsx [3e92fcc3]
    │   ├── loading.tsx [21a574b1]
    │   ├── not-found.tsx [c227e8bb]
    │   ├── page.tsx [415d6b70]
    │   ├── providers.tsx [79fdf7cd]
    │   ├── robots.ts [37a85e04]
    │   ├── sitemap.ts [86c87f9d]
    │   ├── api/ [Merkle: 4547efdf]
    │   │   ├── auth/ [Merkle: 6faa3266]
    │   │   │   ├── callback/ [Merkle: aaf8235a]
    │   │   │   │   └── route.ts [0e14369e]
    │   │   │   ├── github/ [Merkle: 6bbdf066]
    │   │   │   │   └── route.ts [97d77d90]
    │   │   │   └── magic-link/ [Merkle: 0becee21]
    │   │   │       └── route.ts [d3bea4dd]
    │   │   ├── forensics/ [Merkle: 60bc098c]
    │   │   │   └── route.ts [c13a815a]
    │   │   ├── health/ [Merkle: 8ccb5058]
    │   │   │   └── route.ts [036574f2]
    │   │   ├── lemonsqueezy/ [Merkle: 6bb38cc4]
    │   │   │   ├── checkout/ [Merkle: 2684f213]
    │   │   │   │   └── route.ts [fc0becac]
    │   │   │   └── webhook/ [Merkle: 547678e2]
    │   │   │       └── route.ts [87a570da]
    │   │   └── spc/ [Merkle: 9a428d67]
    │   │       └── route.ts [4567087e]
    │   ├── dashboard/ [Merkle: 0c8181fc]
    │   │   ├── layout.tsx [3fe94aa8]
    │   │   ├── loading.tsx [3993509b]
    │   │   ├── page.tsx [a6428a87]
    │   │   ├── account/ [Merkle: c3c0e05b]
    │   │   │   └── page.tsx [fdb6dab2]
    │   │   ├── addons/ [Merkle: 04b54121]
    │   │   │   └── page.tsx [a5ce5d40]
    │   │   ├── billing/ [Merkle: 3d153d68]
    │   │   │   └── page.tsx [b181966b]
    │   │   ├── impact/ [Merkle: 0aa41b67]
    │   │   │   └── page.tsx [d40ec7ed]
    │   │   ├── ledger/ [Merkle: b40a5154]
    │   │   │   └── page.tsx [f3a9254b]
    │   │   └── settings/ [Merkle: 7af7afc6]
    │   │       └── page.tsx [d0b7e9af]
    │   ├── hud/ [Merkle: b6fd2209]
    │   │   └── page.tsx [9026d22f]
    │   ├── login/ [Merkle: ee7a34de]
    │   │   └── page.tsx [9c00159e]
    │   ├── pricing/ [Merkle: 08383495]
    │   │   └── page.tsx [6a59361e]
    │   ├── privacy/ [Merkle: a6e97b73]
    │   │   └── page.tsx [cbe878cc]
    │   ├── security/ [Merkle: 70b6120c]
    │   │   └── page.tsx [dc84b7e0]
    │   └── terms/ [Merkle: 88ee6330]
    │       └── page.tsx [635d95e2]
    ├── components/ [Merkle: e79320f9]
    │   ├── BentoGrid.tsx [6d00f07f]
    │   ├── EvidenceCard.tsx [5a78e5c5]
    │   ├── TerminalDemo.tsx [0b2ef6d3]
    │   ├── activity-ledger.tsx [b7bc1df6]
    │   ├── pulse-widget.tsx [9e155c13]
    │   ├── sanity-alert.tsx [c721da43]
    │   ├── vision-guard.tsx [e08e7b6e]
    │   ├── auth/ [Merkle: 59063bb3]
    │   │   └── AuthSync.tsx [5637fc45]
    │   ├── dashboard/ [Merkle: 83c85a7e]
    │   │   ├── CheckoutButton.tsx [2a8c8761]
    │   │   ├── ForensicOpportunities.tsx [d9da570b]
    │   │   ├── GlobalSidebar.tsx [6fcf0971]
    │   │   ├── StrategicImpact.tsx [a7bdaf57]
    │   │   ├── ValueVault.tsx [cc53372f]
    │   │   ├── billing/ [Merkle: b6970c90]
    │   │   │   └── RefuelAction.tsx [cc8ae2f7]
    │   │   ├── settings/ [Merkle: 4e4eae88]
    │   │   │   ├── DangerZone.tsx [3d880ff0]
    │   │   │   ├── DataSovereignty.tsx [ce9ab912]
    │   │   │   └── GhostModeSection.tsx [18a19c63]
    │   │   └── shell/ [Merkle: 666a4fed]
    │   │       ├── CreditReviver.tsx [c70c2fe1]
    │   │       ├── PageHeader.tsx [4a2d4fbd]
    │   │       ├── SectionShell.tsx [c9efd6e3]
    │   │       └── StatCard.tsx [93b6b126]
    │   ├── observability/ [Merkle: 91d0a6b4]
    │   │   ├── ErrorBoundary.tsx [d62f45f9]
    │   │   └── GlobalErrorBoundary.tsx [7c6251d9]
    │   └── ui/ [Merkle: 5aea680f]
    │       ├── Button.tsx [e3b0c442]
    │       ├── Card.tsx [e3b0c442]
    │       └── RotatingRole.tsx [fb66169f]
    ├── lib/ [Merkle: 313e6a44]
    │   ├── lemonsqueezy.ts [cd7acb23]
    │   ├── telemetry.ts [8fa1418d]
    │   ├── utils.ts [7c8c3dfc]
    │   ├── dal/ [Merkle: 336bfbd9]
    │   │   ├── auth.ts [5b1a4ad3]
    │   │   ├── billing.ts [19d7c7da]
    │   │   ├── ledger.ts [c508be9c]
    │   │   ├── profile.ts [7a473161]
    │   │   └── settings.ts [37e4f576]
    │   └── supabase/ [Merkle: 9c572405]
    │       ├── client.ts [266b27ea]
    │       ├── index.ts [5452ea51]
    │       ├── middleware.ts [1b3458f5]
    │       └── server.ts [cd72b02e]
    └── public/ [Merkle: 634960dd]
        ├── file.svg [2b67812c]
        ├── globe.svg [b614b9bf]
        ├── next.svg [55995dfa]
        ├── vercel.svg [f081337b]
        └── window.svg [644768c4]

```

## 4. SYSTEM PROMPTS (The Instruction)
- **Role:** You represent the Sovereign Will of the repository.
- **Priority:** Trust the Code (Objective) over the Plan (Subjective).
- **Style:** Zero-Latency, High-Precision, No Fluff.

---
*Use this anchor to re-align your weights with the Sovereign Reality.*

#!/bin/bash

# 🦅 Sidelith Shell Hook
# Captures command intent [Software 2.0 Validator]
# Compliance: Zsh (preexec) / Bash (PROMPT_COMMAND)

SIDE_SOCKET="/tmp/side.sock"

_side_send_signal() {
    local cmd="$1"
    local dir=$(pwd)
    local ts=$(date +%s)
    
    # Check if socket exists
    if [ -S "$SIDE_SOCKET" ]; then
        # Construct JSON signal
        local signal="{\"category\": \"shell\", \"tool\": \"shell\", \"action\": \"command\", \"payload\": {\"command\": \"$cmd\", \"cwd\": \"$dir\", \"timestamp\": $ts}}"
        
        # Send to socket (using python for portability since nc -U varies)
        python3 -c "import socket, sys; s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.connect('$SIDE_SOCKET'); s.sendall((sys.argv[1] + '\n').encode()); s.close()" "$signal" > /dev/null 2>&1 &
    fi
}

# Zsh Integration
if [ -n "$ZSH_VERSION" ]; then
    preexec() {
        _side_send_signal "$1"
    }
fi

# Bash Integration
if [ -n "$BASH_VERSION" ]; then
    # We use a trap or DEBUG for pre-execution capture in Bash
    # but PROMPT_COMMAND is safer for post-execution context.
    # For now, let's stick to simple Zsh support as prioritized.
    :
fi

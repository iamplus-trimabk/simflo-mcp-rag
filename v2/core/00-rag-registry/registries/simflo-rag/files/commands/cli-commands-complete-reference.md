# SimFlo RAG CLI Commands - Interactive Guide

## Purpose
Interactive command guide for SimFlo RAG v2. Use search to discover commands and get specific usage information.

## Quick Start (5 Essential Commands)

```bash
# Learn the system
sm_learn

# Get AI assistant guide
sm_guide

# See available registries
sm_registries

# Search for components
sm_search "button" --limit 5

# Get command reference
sm_commands
```

## Command Discovery

### Find Commands by Purpose
```bash
# Registry operations
sm_search "registry create rebuild manage" --registry simflo-rag --limit 5

# Content processing
sm_search "discover fetch extract content" --registry simflo-rag --limit 5

# AI assistant features
sm_search "search get-component list-components context" --registry simflo-rag --limit 5

# System utilities
sm_search "status setup test help" --registry simflo-rag --limit 5
```

### Get Help for Specific Commands
```bash
# Replace [command] with any command name
sm_get "command-help-[command]" --registry simflo-rag

# Examples:
sm_get "command-help-sm_create_registry" --registry simflo-rag
sm_get "command-help-sm_search" --registry simflo-rag
sm_get "command-help-sm_set_context" --registry simflo-rag
```

## Essential Workflows

### Create New Registry
```bash
sm_discover_content --query "react components" --source-type github --limit 5
sm_fetch_content --source "[GITHUB_URL]" --output-dir content/
sm_run_extractors --parallel --output-dir extracted/
sm_create_registry --name my-registry --type component --source-dir extracted/
sm_rebuild_registry --registry my-registry
```

### Component Search & Migration
```bash
sm_set_context reactnative --session-id migration
sm_search "button component equivalent" --limit 5
sm_get "[component-name]" --registry gluestack
sm_list --type ui --platform reactnative --limit 20
```

## Get More Help

```bash
# Show all commands
simflo_help

# AI assistant specific help
sm_ai_help

# System status
sm_registry_status

# Test system
simflo_setup
```

**Tip**: Use `sm_search` with keywords to discover more commands and examples!
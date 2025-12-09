# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an architecture documentation repository for Bharata International Pharmaceutical (BIP). It contains enterprise system architecture specifications in Markdown format, organized by business domain. The documentation is designed to be viewed and edited using Obsidian, which provides graph visualization and linking capabilities.

## Repository Structure

The repository is organized into the following major sections:

- **Application/** - Frontend applications (web and mobile)
- **Core System and Modules/** - API Gateway and core database modules
- **Human Resource Information System/** - HRIS subsystems
- **General Affairs/** - GA systems (procurement, inventory, maintenance, audit)
- **Finance System/** - Financial management and bridging applications
- **Marketing/** - Sales, CRM, and dashboard systems
- **Warehouse/** - Inbound/outbound logistics and warehouse management
- **Third-party Software/** - External integrations (Accurate, CRM vendor)

Key entry points:
- `HOMEPAGE.md` - System architecture overview and key concepts
- `README.md` - Repository setup and collaboration instructions

## Working with Obsidian Documents

This repository uses Obsidian-flavored Markdown with specific conventions:

1. **Internal Links**: Use `[[Document Name]]` syntax for cross-references between documents
   - These create graph relationships in Obsidian
   - Only use Add Link feature in Obsidian for direct dependencies

2. **Image References**: Images are referenced with `![[image-name.png]]` syntax
   - Images may be stored in `.obsidian/` or other directories

3. **Header Style**: Follow the existing header style guide when creating new documents
   - Each system document follows the pattern: `PREFIX - System Name.md`
   - Prefixes: APP (Application), CORE (Core System), DB/MODULE (Database/Module), HRIS, GA, WH, etc.

## Architecture Concepts

### System Layers

1. **APP (Application Layer)**: Web and mobile applications serving as portals to access other systems
   - APP - Web Application (primary portal with login and dashboard)
   - APP - Mobile Application (myBharata app)
   - BASE - Landing Page (base dashboard after login)

2. **CORE System**: Centralized API Gateway
   - CORE - API Master Gateway: Single authentication and routing point for all modules
   - Implements JWT-based authentication with internal key validation
   - Routes requests to MODULE endpoints using internal rerouting
   - [Implementation reference](https://github.com/bip-itteam-internal/api-gateway-test)

3. **MODULE/DB Systems**: Individual microservices with their own databases
   - Each module has isolated NoSQL (MongoDB) databases
   - Modules communicate via internal rerouting with INTERNAL-KEY validation
   - Example: DB - Employees Master Data, DB - Attendance Data

### Key Architecture Patterns

**Database Strategy:**
- Multiple MongoDB NoSQL databases (one per module)
- Employee ID used as natural key (primary key) across systems
- Collections split to manage MongoDB's 16MB document limit
- Cross-module data syncing: modules maintain cached copies of collections they don't own
- Example: Employee Master Data syncs "Company work schedule" from Attendance Data

**Authentication Flow:**
- API Master Gateway handles all authentication
- JWT tokens contain: employee_id, username, system_roles (per-system role mappings)
- Gateway adds custom headers for downstream modules
- Modules validate INTERNAL-KEY from gateway, bypass user authentication

**Internal Rerouting:**
- Modules can call other modules directly without going through gateway authentication
- Uses shared INTERNAL-KEY for authorization between services
- Implemented via [shared-library](https://github.com/bip-itteam-internal/api-gateway-test)

## Document Conventions

When creating or modifying architecture documents:

1. **Status Tracking**: Use checkbox lists for requirements and dependencies
   - `- [x]` for completed items
   - `- [ ]` for pending items

2. **Database Structures**: Use JSON code blocks with MongoDB syntax
   - Include field comments for clarity
   - Show example values
   - Note encryption/hashing where applicable

3. **Cross-References**: Link to related systems using `[[System Name]]` syntax

4. **Pending Items**: Mark incomplete sections with headers like "Pending Details" or "Consideration"

5. **External Links**: Reference external resources (Google Drive, GitHub repos) with full URLs

## Common Workflows

### Viewing the Documentation
1. Open the repository in Obsidian (instructions in README.md)
2. Start from HOMEPAGE.md for system overview
3. Use graph view to explore system relationships

### Publishing Changes
- Git workflow: clone, edit in Obsidian, commit, and push changes
- Pull regularly to stay synchronized
- Offline HTML export available at `.export/architecture-draft.html`
- Live version: http://architecture.bharatainternasional.com/

### Understanding System Dependencies
- Check "Dependencies" section in each document
- Follow checkbox links to dependent systems
- Use "Big Pictures" documents for subsystem overviews (e.g., HRIS - Big Pictures, GA - Big Pictures)

## Current Implementation Status

According to the recent commits and HOMEPAGE.md:

**Implemented (Priority Systems):**
- MODULE - Employees Master Data (implementing)
- CORE - API Master Gateway (polishing)
- APP - Web Application (implementing) with features:
  - Login with username/password
  - HRIS employee master data management
  - HRIS attendance monitoring
  - HRIS holiday list management

**In Design/Planning:**
- BASE - Landing Page
- Various HRIS subsystems (Payroll, Recruitment, Training, etc.)
- Finance system (new ground-up implementation)
- Sales/Marketing systems (CRM, dashboards, incentives)
- Warehouse management
- General Affairs systems

## References

- API Gateway implementation: https://github.com/bip-itteam-internal/api-gateway-test
- HRD employee data examples: https://drive.google.com/drive/folders/1DlL37IECH2i1e3-3oypd912AbcPU84nX
- CRM monitoring dashboard: https://monitoring.hubcrm.bharatainternasional.com/

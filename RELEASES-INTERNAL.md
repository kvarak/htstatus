# Internal Releases

**Purpose**: Technical release notes for developers and administrators
**Audience**: Development team and system administrators
**Format**: Technical details, infrastructure changes, and internal improvements

*For user-facing changes, see [RELEASES.md](RELEASES.md)*

---

## 3.15 - February 2026

**Deployment Architecture Simplification**
- Refactored deployment system to follow separation of concerns pattern
- Moved deploy.sh from root to scripts/deployment/ directory for better organization
- Created 5 reusable Makefile deployment targets: deploy-prepare, deploy-sync, deploy-docs, deploy-migrate, deploy-finalize
- Added intelligent make deploy target with git-aware behavior (dry-run if not pushed, force override with FORCE_DEPLOY=true)
- Applied simplification hierarchy achieving 70% code reduction (400+ lines → 120 lines)
- Enhanced DEPLOYMENT.md with comprehensive deployment architecture documentation
- Achieved single source of truth for deployment logic in Makefile

**Development Workflow Improvements**
- Restructured commit workflow in prompts.json from 14-step list to 7-phase structure
- Separated internal vs user-facing release documentation workflows
- Always update RELEASES-INTERNAL.md for all tagged releases
- Only update RELEASES.md for user-visible features (UI, new functionality, workflow improvements)
- Eliminated redundant instructions and improved workflow clarity

## 3.14 - February 2026

**User Analytics & Activity Tracking**
- Enhanced comprehensive activity tracking system with 5 new user behavior counters (settings, changes, feedback, formation, stats)
- Added 15 interactive Chart.js dashboards for detailed user engagement analysis
- Implemented database migrations for expanded activity tracking schema
- Created comprehensive debug page with admin filtering and real-time data visualization
- Added activity tracking to all blueprint routes for complete user journey mapping

**Technical Infrastructure**
- Enhanced User model with specialized activity tracking methods
- Expanded database schema with new tracking fields and proper migrations
- Improved version format consistency across all release documentation
- Enhanced test coverage with improved test logic for automation scripts

## 3.13 - February 2026

**Infrastructure & Automation**
- Added comprehensive release automation system with version detection
- Implemented automated git tagging and release documentation generation
- Created make targets for standardized release workflow (release-detect, release-notes, release-tag)
- Enhanced deployment automation with make target integration
- Modernized all script calls to use unified make-based workflow

**Development Workflow**
- Added db-apply make target for production-safe database migrations
- Updated commit prompt workflow to use make commands instead of direct scripts
- Enhanced project documentation with new automation procedures
- Improved error messages and help text to reference standardized commands

**Technical Improvements**
- Generated JSON timeline data for releases and changelog integration
- Created dual documentation system (user-facing RELEASES.md + technical RELEASES-INTERNAL.md)
- Enhanced UI consistency and component cleanup
- Various utility and test coverage improvements

## 3.12 - February 2026

- Extracted reusable team timeline utility for better code organization
- Enhanced timeline functionality with improved component architecture

## 3.11 - February 2026

- Implemented PWA session persistence with enhanced state management
- Improved service worker caching strategies and offline functionality

## 3.10 - February 2026

- Added admin feedback navigation indicators with conditional display logic
- Enhanced feedback system status tracking and administrative controls

## 3.9 - January 2026

- Implemented feedback archiving system with database schema updates
- Added archived field migration and lifecycle management

## 3.8 - January 2026

- Built comprehensive user feedback system with voting mechanism
- Database schema expansion for community features and admin controls
- OAuth integration improvements and session security enhancements

## 3.7 - January 2026

- Developed formation testing system with tactical validation
- Enhanced team formation capabilities with position analysis
- Improved CHPP API integration for formation data

## 3.6 - January 2026

- Enhanced database management with automated backup scripts
- Improved migration safety and data integrity validation
- Added comprehensive database monitoring and maintenance tools

## 3.5 - January 2026

- Implemented automatic default player group creation system
- Database schema updates for group management and user onboarding
- Enhanced user registration flow with sensible defaults

## 3.4 - January 2026

- Added group color support to timeline feature with CSS integration
- Enhanced timeline visualization with improved data organization
- Frontend styling improvements and responsive design updates

## 3.3 - January 2026

- Implemented architectural improvement framework
- Enhanced code organization standards and development workflows
- Improved testing infrastructure and quality gates

## 3.2 - January 2026

- Unified UI component classes across Flask templates
- Consolidated CSS architecture and design system implementation
- Enhanced maintainability through consistent styling patterns

## 3.1 - January 2026

- Implemented automatic version counting system with git integration
- Enhanced development workflow with improved version tracking
- Added feature detection and release automation tools

## 3.0 - January 2026

- Fixed critical Hattrick API integration issues with pychpp updates
- Enhanced database migration system with comprehensive safety checks
- Improved authentication flow and session management
- Added comprehensive error handling and logging improvements

## 2.0 - December 2025

- Complete architectural redesign with modern development stack
- Migrated to React frontend with TypeScript integration
- Enhanced build system with Vite and improved development workflow
- Implemented comprehensive testing infrastructure

## 1.0 - February 2023

- Initial Flask application architecture with SQLAlchemy ORM
- Hattrick OAuth integration using pychpp library
- Database schema design for player and team data storage
- Core web interface implementation with Bootstrap styling
- Basic CHPP API integration for data synchronization

## 0.0 - June 2020

- Project inception and repository initialization
- First commit establishing the foundation for Hattrick team management tools
- Beginning of the journey to build comprehensive player statistics platform

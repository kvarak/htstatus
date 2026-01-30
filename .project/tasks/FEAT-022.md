# FEAT-022: User Feedback System with Voting and Comments

## Problem Statement
Users currently have no way to provide feedback, report bugs, request features, or share ideas within the application. This limits community engagement and makes it difficult to prioritize development based on user needs. A simple, Fider-inspired feedback system would allow users to contribute to the product direction while maintaining the hobby project's simplicity.

Hattrick managers are passionate users who often have valuable insights about missing features, desired improvements, and bugs they encounter. Capturing this feedback systematically would help prioritize development efforts and build community engagement.

## Implementation
Create a simple feedback system inspired by Fider but much simpler, focusing on core functionality that aligns with the hobby project philosophy.

### Core Features
1. **Feedback Page**: Simple form for submitting bugs, features, and ideas
2. **Navigation**: Add "Feedback" link to top-right navigation
3. **Public Visibility**: All logged-in users can see all feedback
4. **Voting System**: Users can vote on feedback items
5. **Comments**: Users can comment on feedback items
6. **Admin Controls**: Admin comments highlighted, marking/archiving capabilities

### Technical Implementation
- **Database Models**:
  - `Feedback` (title, description, type [bug/feature/idea], status, author, votes, created_at)
  - `FeedbackComment` (feedback_id, author, content, is_admin, created_at)
  - `FeedbackVote` (feedback_id, user_id, vote_type [up/down])
- **Routes**: `/feedback` (list), `/feedback/new` (form), `/feedback/<id>` (details)
- **UI**: Use existing design system with football green theme
- **Permissions**: Logged-in users only, admin controls for status/archiving
- **Simplicity**: No complex features like tags, categories, or advanced filtering

### Simplification Focus
- **No External Dependencies**: Use existing Flask/SQLAlchemy/Bootstrap stack
- **Minimal UI**: Simple forms and lists, no complex interfaces
- **Basic Admin**: Simple status toggles, no complex workflow management
- **Core Voting**: Simple up/down votes, no complex rating systems

## Acceptance Criteria
- [ ] "Feedback" link appears in top-right navigation for logged-in users
- [ ] Feedback submission form with title, description, and type selection
- [ ] Public feedback list showing all submissions with vote counts
- [ ] Individual feedback detail pages with comments section
- [ ] Users can vote (up/down) on feedback items (one vote per user)
- [ ] Users can add comments to feedback items
- [ ] Admin comments display with different styling (e.g., background color)
- [ ] Admin can mark feedback status (open/planned/in-progress/completed/archived)
- [ ] Admin can archive feedback items
- [ ] Responsive design matching existing UI patterns
- [ ] Database migration for new tables
- [ ] Test coverage for all new functionality
- [ ] No external API dependencies or complex features
- [ ] Performance: Page loads under 2 seconds with 100+ feedback items

# CHPP API Reference: Staff Avatars

**Purpose**: Visual avatar data for team staff members with customizable appearance layers
**Endpoint**: `/chppxml.ashx?file=staffavatars`
**Authentication**: OAuth required
**Rate Limiting**: Standard CHPP limits apply

## Overview

The Staff Avatars endpoint provides detailed visual avatar information for team coaching staff, including trainers and specialists. This endpoint enables rich visual representation of staff members through layered avatar systems, with supporter-tier dependent visual quality.

## Request Parameters

### Required
- `file=staffavatars` - Specifies the staff avatars endpoint

### Optional
- `version` - API version (latest recommended)
- `teamId` - Target team identifier (unsigned integer)
  - **Default**: Authenticated user's primary club senior team ID
  - **Access**: Can access any team for public avatar display
  - **Usage**: Staff avatar visualization and team presentation

## Response Structure

### Trainer Avatar Data
```xml
<HattrickData>
    <Trainer>
        <TrainerId>123456</TrainerId>
        <Avatar>
            <BackgroundImage>https://www.hattrick.org/pic/avatar/backgrounds/bg_001.png</BackgroundImage>
            <Layer x="50" y="30">
                <Image>https://www.hattrick.org/pic/avatar/hair/hair_023.png</Image>
            </Layer>
            <Layer x="45" y="40">
                <Image>https://www.hattrick.org/pic/avatar/eyes/eyes_012.png</Image>
            </Layer>
            <Layer x="48" y="55">
                <Image>https://www.hattrick.org/pic/avatar/mouth/mouth_008.png</Image>
            </Layer>
        </Avatar>
    </Trainer>
</HattrickData>
```

### Staff Members Avatar Data
```xml
<StaffMembers>
    <Staff>
        <StaffId>789012</StaffId>
        <Avatar>
            <BackgroundImage>https://www.hattrick.org/pic/avatar/backgrounds/bg_002.png</BackgroundImage>
            <Layer x="52" y="25">
                <Image>https://www.hattrick.org/pic/avatar/accessories/hat_005.png</Image>
            </Layer>
            <Layer x="50" y="32">
                <Image>https://www.hattrick.org/pic/avatar/hair/hair_015.png</Image>
            </Layer>
            <Layer x="47" y="42">
                <Image>https://www.hattrick.org/pic/avatar/eyes/eyes_007.png</Image>
            </Layer>
        </Avatar>
    </Staff>
</StaffMembers>
```

## Avatar System Architecture

### Layer-Based Rendering
- **BackgroundImage** - Base card background with team context
- **Layer Elements** - Positioned avatar components with x,y coordinates
- **Layering Order** - XML order determines visual stacking (later elements on top)
- **Coordinate System** - Pixel-based positioning for precise avatar assembly

### Staff Member Types
- **Trainer** - Head coach with dedicated TrainerId reference
- **Staff Members** - Specialists (doctors, psychologists, etc.) with StaffId references
- **Visual Distinction** - Different avatar styling based on staff role and team supporter status

## Supporter Tier Integration

### Visual Quality Levels
```python
def determine_avatar_quality(team_supporter_tier, staff_member):
    """Determine avatar visual quality based on supporter status"""
    if team_supporter_tier in ['platinum', 'gold', 'silver']:
        return {
            'background_type': 'full_custom',
            'layer_count': 'unlimited',
            'detail_level': 'high',
            'customization_options': 'full'
        }
    else:
        return {
            'background_type': 'silhouette',
            'layer_count': 'basic',
            'detail_level': 'standard',
            'customization_options': 'limited'
        }
```

### Non-Supporter Display
- **Silhouette Backgrounds** - Generic shadow-style representations
- **Limited Layers** - Basic avatar components only
- **Team Branding** - Maintains team identity without premium customization

## Implementation Guidelines

### Avatar Rendering System
```python
def render_staff_avatar(avatar_data):
    """Render complete staff member avatar from layer data"""
    avatar_canvas = {
        'background': avatar_data['BackgroundImage'],
        'layers': [],
        'dimensions': {'width': 100, 'height': 120}  # Standard avatar size
    }

    for layer in avatar_data['Layer']:
        avatar_canvas['layers'].append({
            'image_url': layer['Image'],
            'position': {
                'x': int(layer['@x']),
                'y': int(layer['@y'])
            },
            'z_index': len(avatar_canvas['layers'])  # Layer order
        })

    return avatar_canvas
```

### Staff Identification Integration
```python
def create_staff_directory(trainer_data, staff_members_data):
    """Create visual staff directory with avatars and roles"""
    staff_directory = {
        'head_coach': {
            'id': trainer_data['TrainerId'],
            'title': 'Head Coach',
            'avatar': render_staff_avatar(trainer_data['Avatar']),
            'role_type': 'trainer'
        },
        'specialists': []
    }

    for staff in staff_members_data:
        staff_directory['specialists'].append({
            'id': staff['StaffId'],
            'title': determine_staff_role(staff['StaffId']),  # Cross-reference with Club endpoint
            'avatar': render_staff_avatar(staff['Avatar']),
            'role_type': 'specialist'
        })

    return staff_directory
```

## Strategic Usage Guidelines

### Team Presentation Features
1. **Staff Directory Display** - Visual team hierarchy with avatar representations
2. **Coaching Staff Cards** - Enhanced staff member profiles with visual identity
3. **Team About Page** - Complete staff visualization for team presentation

### Integration Opportunities
- **Club Endpoint Integration** - Combine with staff roles and specializations
- **Team Details Enhancement** - Visual staff representation in team overviews
- **Training Integration** - Associate trainer avatars with training reports and progress

### UI Enhancement Applications
- **Dashboard Personalization** - Staff avatar display in team management interfaces
- **Training Reports** - Visual trainer identification in progress reports
- **Staff Management** - Enhanced staff hiring and management interfaces

## Performance & Caching Strategy

### Image Asset Management
```python
def cache_staff_avatars(team_id, avatar_data):
    """Efficient caching strategy for staff avatars"""
    cache_strategy = {
        'base_images': {
            'cache_duration': '7_days',  # Backgrounds change infrequently
            'storage_type': 'cdn_cache'
        },
        'layer_components': {
            'cache_duration': '24_hours',  # Individual layers may update
            'storage_type': 'local_cache'
        },
        'rendered_avatars': {
            'cache_duration': '1_hour',  # Complete avatars for quick display
            'storage_type': 'memory_cache',
            'invalidation_trigger': 'staff_changes'
        }
    }

    return cache_strategy
```

### Loading Optimization
- **Progressive Loading** - Background first, then layer components
- **Placeholder Strategy** - Generic silhouettes during avatar assembly
- **Batch Requests** - Group avatar requests for team efficiency

## Data Validation & Error Handling

### Avatar Data Validation
- **Image URL Verification** - Validate avatar component URLs are accessible
- **Layer Position Bounds** - Ensure x,y coordinates are within valid ranges
- **Staff ID Consistency** - Cross-reference with team staff data

### Fallback Strategies
- **Missing Layers** - Graceful handling of unavailable avatar components
- **Network Failures** - Default to cached or placeholder avatars
- **Supporter Downgrades** - Handle transitions between avatar quality levels

## Integration with Team Features

### Staff Management Enhancement
- **Visual Staff Selection** - Avatar-based staff hiring and management interfaces
- **Role Identification** - Quick visual recognition of staff specializations
- **Team Chemistry Display** - Visual representation of staff relationships

### Training System Integration
- **Trainer Recognition** - Associate specific trainers with training reports
- **Progress Visualization** - Link trainer avatars to training effectiveness
- **Staff Performance** - Visual staff evaluation and feedback systems

## OAuth & Access Control

### Authentication Requirements
- **Basic Access** - View avatars for any team (public visual data)
- **No Special Scopes** - Standard authentication sufficient for avatar display
- **Rate Limiting** - Standard limits apply for avatar data requests

### Privacy Considerations
- **Public Display** - Avatar data is generally publicly accessible
- **Team Branding** - Avatars reflect team identity and supporter investment
- **Visual Consistency** - Maintain avatar quality standards across supporter tiers

## Related Endpoints
- **Club** (`file=club`) - Staff roles and specialization details
- **Team Details** (`file=teamdetails`) - Team context and supporter tier information
- **Training** (`file=training`) - Trainer performance and training effectiveness

---

*This specialized avatar endpoint enables enhanced visual team representation and staff identification for improved team management interfaces and presentation features.*

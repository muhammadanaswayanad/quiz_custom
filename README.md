# Quiz Engine Pro - Odoo 17 Module

A comprehensive, standalone quiz engine for Odoo 17 Community Edition that provides advanced question types and interactive features.

## Features

### Question Types
- **Multiple Choice (Single Answer)** - Traditional radio button selection
- **Multiple Choice (Multiple Answers)** - Checkbox-based selection
- **Fill in the Blanks** - Text input fields within questions
- **Match the Following** - Drag and connect related items
- **Drag and Drop into Zones** - Drag items into designated areas
- **Drag and Drop Into Text** - Interactive text with draggable tokens

### Core Functionality
- ✅ Quiz creation and management
- ✅ Question sequencing and randomization
- ✅ Time limits and attempt restrictions
- ✅ Real-time scoring and evaluation
- ✅ Session tracking for anonymous and logged-in users
- ✅ Responsive frontend interface
- ✅ SEO-friendly URLs with custom slugs

## Installation

1. Copy the `quiz_engine_pro` folder to your Odoo addons directory
2. Update the addons list in Odoo
3. Install the "Quiz Engine Pro" module

## Module Structure

```
quiz_engine_pro/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── quiz.py          # Main quiz model
│   ├── question.py      # Question types and choices
│   └── response.py      # Sessions and answers
├── views/
│   ├── quiz_views.xml
│   ├── question_views.xml
│   ├── session_views.xml
│   └── website_templates.xml
├── controllers/
│   ├── __init__.py
│   └── main.py          # Frontend routes
├── security/
│   └── ir.model.access.csv
└── static/src/
    ├── js/
    │   └── drag_into_text.js
    └── css/
        └── quiz_styles.css
```

## Models Overview

### quiz.quiz
Main quiz container with configuration options.

**Key Fields:**
- `name` - Quiz title
- `slug` - URL-friendly identifier
- `is_published` - Publication status
- `randomize_questions` - Question order randomization
- `time_limit` - Maximum time in minutes
- `passing_score` - Minimum percentage to pass

### quiz.question
Individual questions with type-specific configurations.

**Question Types:**
- `mcq_single` - Single correct answer
- `mcq_multi` - Multiple correct answers
- `fill_blank` - Text input blanks
- `match` - Matching pairs
- `drag_zone` - Drag into zones
- `drag_into_text` - Drag tokens into text placeholders

### quiz.session
Tracks individual quiz attempts and scoring.

**Features:**
- Session state management
- Time tracking
- Score calculation
- Anonymous user support

## Usage Guide

### Creating a Quiz

1. Go to Quiz Engine → Quizzes
2. Click "Create" 
3. Fill in quiz details:
   - Name and description
   - Time limit (optional)
   - Passing score percentage
   - Randomization settings
4. Save and add questions

### Adding Questions

1. Open a quiz record
2. Go to "Questions" tab or click "Manage Questions"
3. Select question type
4. Enter question content using HTML editor
5. Configure type-specific options:

#### Multiple Choice
- Add choices in the "Answer Options" tab
- Mark correct answers with checkbox

#### Drag Into Text
- Use `{{1}}`, `{{2}}` placeholders in question HTML
- Add drag tokens in "Drag Tokens" tab
- Set correct token for each blank number

### Frontend Access

Quiz URLs follow the pattern: `/quiz/<slug>`

Example: `/quiz/javascript-basics`

## Technical Details

### Drag and Drop Implementation

The drag-into-text feature uses native HTML5 drag and drop:

1. Question HTML contains placeholders: `{{1}}`, `{{2}}`
2. JavaScript converts these to drop zones
3. Tokens are rendered as draggable elements
4. Answer data is stored as JSON: `{"1": "token1", "2": "token2"}`

### Scoring System

- Each question has a configurable point value
- Answers are evaluated using question-specific logic
- Partial scoring supported for some question types
- Final percentage calculated for pass/fail determination

### Session Management

- Unique tokens identify quiz sessions
- State tracking: draft → in_progress → completed/expired
- Anonymous user support with optional participant info
- Time limit enforcement with automatic expiry

## API Endpoints

### Frontend Routes
- `GET /quiz` - List published quizzes
- `GET /quiz/<slug>` - Quiz start page
- `POST /quiz/<slug>/take` - Begin quiz session
- `GET /quiz/session/<token>/question/<id>` - Question display
- `POST /quiz/session/<token>/answer` - Submit answer (JSON)
- `POST /quiz/session/<token>/complete` - Complete quiz
- `GET /quiz/session/<token>/results` - View results

## Customization

### Adding New Question Types

1. Add new type to `quiz.question.type` selection
2. Create supporting model if needed (like `quiz.drag.token`)
3. Implement evaluation logic in `evaluate_answer()`
4. Add frontend template and JavaScript handling
5. Update backend form views

### Styling Customization

Modify `/static/src/css/quiz_styles.css` for visual customization:
- Colors and branding
- Layout adjustments
- Mobile responsiveness
- Animation effects

## Security

- Public access for taking quizzes
- Admin-only backend management
- Session token validation
- XSS protection with proper HTML escaping

## Dependencies

- Odoo 17 Community Edition
- Base modules: `base`, `web`, `website`
- No external dependencies

## Roadmap

### Planned Features
- [ ] Advanced analytics dashboard
- [ ] Question banks and categories
- [ ] Bulk question import/export
- [ ] Certificate generation
- [ ] Integration with LMS systems
- [ ] Mobile app support
- [ ] Advanced reporting
- [ ] Question difficulty ratings
- [ ] Adaptive testing

### Performance Optimizations
- [ ] Question preloading
- [ ] Answer caching
- [ ] Database indexing
- [ ] CDN asset delivery

## Contributing

1. Fork the repository
2. Create feature branch
3. Follow Odoo coding standards
4. Add tests for new functionality
5. Submit pull request

## License

LGPL-3 (same as Odoo Community Edition)

## Support

For issues and questions:
- Check existing GitHub issues
- Create new issue with detailed description
- Include Odoo version and error logs
- Provide steps to reproduce

## Changelog

### Version 17.0.1.0.0
- Initial release
- All core question types implemented
- Frontend quiz interface
- Session tracking and scoring
- Basic analytics

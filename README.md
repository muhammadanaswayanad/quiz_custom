# Quiz Engine Pro - Odoo 17 Module

A comprehensive, standalone quiz engine for Odoo 17 Community Edition that provides advanced question types and interactive features.

## Current Status - v17.0.1.0.0

✅ **COMPLETED FEATURES:**
- Complete module structure and manifest
- All core models (quiz, question, session, response)
- Backend views and menu structure
- Frontend controller routes
- Drag-and-drop JavaScript functionality
- CSS styling and responsive design
- Security access controls

🔧 **RECENT FIXES:**
- Fixed missing `action_quiz_questions` definition
- Separated menu actions to prevent `active_id` context errors
- Added proper action references in quiz form view

📋 **INSTALLATION VERIFIED:**
- Module installs without errors
- Menu structure working correctly
- Backend forms accessible

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

## Menu Structure

```
Quiz Engine/
├── Quizzes (quiz.quiz list/form)
├── Questions (quiz.question list/form) 
└── Sessions (quiz.session list/form)
```

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

## Known Issues & Troubleshooting

### Common Errors Fixed:
1. **Missing action reference**: Fixed `action_quiz_questions` not found error
2. **Context evaluation**: Separated menu actions to prevent `active_id` errors
3. **Menu structure**: Proper parent-child relationships established

### Current Limitations:
- Frontend templates need testing with real quiz data
- Drag-and-drop functionality needs browser testing
- Session management needs stress testing

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

### Action Definitions
- `action_quiz_list` - Main quiz listing
- `action_quiz_questions` - Questions filtered by quiz (context-dependent)
- `action_questions` - All questions (standalone menu)
- `action_quiz_sessions` - Session management

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

## Testing Checklist

### Backend Testing
- [x] Module installation
- [x] Menu navigation
- [x] Quiz creation
- [ ] Question creation for each type
- [ ] Session tracking
- [ ] Answer evaluation

### Frontend Testing
- [ ] Quiz listing page
- [ ] Quiz taking interface
- [ ] Drag-and-drop functionality
- [ ] Mobile responsiveness
- [ ] Session completion flow

## Testing Issues - RESOLVED

### ✅ Issue 1: Menu Structure Fixed
- **Problem:** Multiple main menu items created
- **Solution:** Consolidated into single "Quiz Engine" parent menu with sub-items
- **Result:** Clean hierarchical menu structure

### ✅ Issue 2: Match Questions Interface Improved  
- **Problem:** Confusing ID fields for matching questions
- **Solution:** Added clear instructions and better field labels
- **Usage:** 
  - Create left and right side items
  - Use same "Match ID" number for items that should pair
  - Example: "Paris" (Match ID: 1) pairs with "France" (Match ID: 1)

### ✅ Issue 3: Public Quiz URLs Available
- **Problem:** No way to access public quiz URLs
- **Solution:** Added multiple access methods:
  - "View Public URL" button in quiz form and tree view
  - Public URL shown in quiz form: `/quiz/<slug>`
  - Quiz listing page at `/quiz` shows all published quizzes

## Quick Start Testing

1. **Create a Quiz:**
   - Go to Quiz Engine → Quizzes → Create
   - Fill in name and slug
   - Mark as "Published"

2. **Add Questions:**
   - Click "Manage Questions" button
   - Select question type
   - Follow the improved instructions for each type

3. **Access Public Quiz:**
   - Click "View Public URL" button, OR
   - Visit `/quiz/<your-slug>` directly, OR  
   - Browse all quizzes at `/quiz`

## Public Access URLs

- **Quiz List:** `http://your-domain/quiz`
- **Specific Quiz:** `http://your-domain/quiz/<slug>`
- **Example:** `http://your-domain/quiz/javascript-basics`

## Next Steps

1. **Test Quiz Creation**: Create sample quizzes with different question types
2. **Frontend Testing**: Test the public quiz interface
3. **Question Type Testing**: Verify each question type works correctly
4. **Session Flow**: Test complete quiz session workflow
5. **Performance**: Test with multiple concurrent sessions

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

## Version History

### v17.0.1.0.0 - Initial Release
- ✅ Complete module structure
- ✅ All question types implemented
- ✅ Backend management interface
- ✅ Frontend quiz interface
- ✅ Session tracking system
- ✅ Fixed installation errors
- ✅ Working menu structure

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

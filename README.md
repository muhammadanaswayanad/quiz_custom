# Quiz Engine Pro

A comprehensive quiz engine module for Odoo 17 Community Edition with advanced question types and interactive features.

## Features

### Question Types
- **Multiple Choice (Single Answer)** - Radio button selection
- **Multiple Choice (Multiple Answers)** - Checkbox selection  
- **Fill in the Blanks** - Text input for missing words
- **Match the Following** - Drag and drop matching pairs
- **Drag and Drop into Text** - Interactive token placement
- **Drag and Drop into Zones** - Zone-based placement

### Core Functionality
- **Public Quiz Access** - Share quizzes via public URLs
- **Real-time Scoring** - Automatic answer evaluation
- **Session Tracking** - Complete quiz attempt monitoring
- **Responsive Design** - Mobile-friendly interface
- **Progress Navigation** - Next/Previous question controls
- **Results Dashboard** - Detailed performance analytics

## Installation

1. Clone or download the module to your Odoo addons directory:
   ```bash
   /home/tl/code/custom_addons/quiz_engine_pro/
   ```

2. Update your Odoo configuration to include the custom addons path

3. Restart Odoo server

4. Go to Apps menu and install "Quiz Engine Pro"

## Quick Start

### Creating a Quiz

1. Navigate to **Quiz Engine** menu in Odoo backend
2. Click **Quizzes** → **Create**
3. Fill in quiz details:
   - Title and description
   - Passing score percentage
   - Time limit (optional)
   - Publication settings

### Adding Questions

1. Open your quiz and go to **Questions** tab
2. Click **Add a line** to create new questions
3. Select question type and configure:
   - **MCQ**: Add choices and mark correct answers
   - **Fill Blanks**: Use `{{1}}`, `{{2}}` placeholders and define answers
   - **Matching**: Create left-right text pairs
   - **Drag & Drop**: Define tokens and target positions

### Publishing Quiz

1. Set quiz status to **Published**
2. Click **View Public URL** to get shareable link
3. Share URL with participants

## Usage

### Public Quiz Taking

1. Participants access quiz via public URL
2. Enter name (email optional)
3. Navigate through questions using Next/Previous
4. Submit quiz to see results
5. View score and performance breakdown

### Backend Management

- **Quiz Analytics** - Track all sessions and responses
- **Question Bank** - Reuse questions across multiple quizzes
- **Session Monitoring** - Real-time participant progress
- **Results Export** - Download quiz performance data

## Technical Details

### Models
- `quiz.quiz` - Main quiz container
- `quiz.question` - Question definitions with type-specific fields
- `quiz.session` - Individual quiz attempts
- `quiz.response` - Answer storage per question
- `quiz.choice` - Multiple choice options
- `quiz.match.pair` - Matching question pairs
- `quiz.drag.token` - Drag and drop elements
- `quiz.fill.blank.answer` - Fill-in-the-blank solutions

### URL Structure
- `/quiz` - Public quiz listing
- `/quiz/{slug}` - Quiz information page
- `/quiz/{slug}/start` - Begin quiz session
- `/quiz/{slug}/question/{num}` - Question display
- `/quiz/session/{token}/complete` - Results page

### Security
- Public access for quiz taking
- Admin access for quiz management
- Session token-based security
- CSRF protection disabled for public forms

## Development

### Requirements
- Odoo 17.0 Community Edition
- Python 3.8+
- Modern web browser with JavaScript enabled

### Module Structure
```
quiz_engine_pro/
├── __init__.py
├── __manifest__.py
├── controllers/
│   └── main.py
├── models/
│   ├── quiz.py
│   ├── question.py
│   └── response.py
├── security/
│   └── ir.model.access.csv
├── static/
│   ├── description/icon.png
│   └── src/
│       ├── css/quiz_styles.css
│       └── js/drag_into_text.js
├── views/
│   ├── quiz_views.xml
│   ├── question_views.xml
│   ├── session_views.xml
│   └── website_templates.xml
└── README.md
```

### Customization

The module supports extensive customization:

- **Custom Question Types**: Extend the question model
- **Theming**: Modify CSS in `static/src/css/`
- **Scoring Logic**: Customize evaluation methods
- **Report Templates**: Create custom result layouts

## Troubleshooting

### Common Issues

1. **Quiz not accessible publicly**
   - Check quiz is marked as "Published"
   - Verify website module is installed

2. **JavaScript errors**
   - Clear browser cache
   - Check console for specific errors
   - Ensure all dependencies loaded

3. **Session expired errors**
   - Module uses `csrf=False` for public access
   - Check Odoo session configuration

### Support

For technical support or feature requests:
- Review the WORKLOG.md for development history
- Check Odoo logs for detailed error messages
- Verify all dependencies are properly installed

## Version History

- **17.0.1.0.1** - Initial release
  - Complete Odoo 17 compatibility
  - All question types implemented
  - Public quiz interface
  - Session management
  - Results tracking

## License

LGPL-3 - See LICENSE file for details

## Author

Developed for Tijus Academy with comprehensive quiz functionality and modern web interface.
- ✅ Updated Odoo 17 compatibility
- ✅ Improved question form interface

### v17.0.1.0.0 - Initial Release
- ✅ Complete module structure
- ✅ All question types implemented
- ✅ Backend management interface
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

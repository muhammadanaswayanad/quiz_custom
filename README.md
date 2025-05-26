# Quiz Engine Pro

A modular, extensible quiz system for Odoo 17 Community Edition. This README is designed to help both human and AI developers understand, maintain, and extend the module.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Directory Structure](#directory-structure)
- [Key Models](#key-models)
- [Frontend & Backend](#frontend--backend)
- [Development Guidelines](#development-guidelines)
- [Extending the Module](#extending-the-module)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Quiz Engine Pro enables advanced quiz creation, management, and analytics in Odoo. It supports multiple question types, user attempts, and detailed reporting. The codebase is modular and follows Odoo best practices for easy extension.

---

## Features

- Create and manage quizzes with time limits, login requirements, and attempt tracking
- Multiple question types: Multiple Choice (MCQ), Fill in the Blanks, Match the Following, Drag and Drop
- Randomization of questions and answers
- User attempt tracking and scoring
- Frontend quiz execution with website integration
- Analytics and exportable reports
- Role-based access control

---

## Installation

1. Copy `quiz_custom` to your Odoo addons directory.
2. Update the Odoo app list.
3. Install "Quiz Engine Pro" from the Apps menu.

**Dependencies:**  
- Odoo 17 Community Edition  
- Python 3.8+  
- Modules: `base`, `web`, `website`

---

## Directory Structure

```
quiz_custom/
├── __init__.py
├── __manifest__.py
├── README.md
├── controllers/
│   └── main.py
├── models/
│   ├── __init__.py
│   ├── quiz.py
│   ├── question.py
│   ├── session.py
│   └── response.py
├── static/
│   └── src/js/quiz_frontend.js
├── upgrade/
│   └── upgrade_response_model.py
├── views/
│   ├── quiz_views.xml
│   ├── question_views.xml
│   ├── session_views.xml
│   ├── quiz_templates.xml
│   └── quiz_menus.xml
└── security/
    ├── quiz_security.xml
    └── ir.model.access.csv
```

---

## Key Models

- **quiz.quiz**: The quiz itself (title, description, settings, etc.)
- **quiz.question**: A question belonging to a quiz (type, content, points, etc.)
- **quiz.answer.option**: Answer options for MCQ/drag questions
- **quiz.match.pair**: Pairs for matching questions
- **quiz.blank.expected**: Expected answers for fill-in-the-blank
- **quiz.session**: A user's attempt at a quiz
- **quiz.response**: A user's response to a question in a session

---

## Frontend & Backend

- **Frontend**: Website templates (`quiz_templates.xml`) and JavaScript (`quiz_frontend.js`) provide the quiz-taking interface, including drag-and-drop, timers, and dynamic forms.
- **Backend**: Models and business logic in `models/`, admin views in `views/`, and security in `security/`.

---

## Development Guidelines

- Follow Odoo's modular structure and naming conventions.
- Use computed fields and related fields for dynamic data.
- Use `@api.depends` for field dependencies.
- Use `@api.model_create_multi` for batch creation.
- Use `sudo()` carefully, especially in controllers.
- Add new question types by extending `quiz.question` and updating templates and evaluation logic.
- For frontend changes, update both the XML templates and the JS widgets as needed.

---

## Extending the Module

**To add a new question type:**
1. Add a new selection value to `question_type` in `quiz.question`.
2. Add supporting fields/models if needed.
3. Update the backend evaluation logic in `quiz.response`.
4. Update the website templates to render the new type.
5. Update JS if frontend interactivity is required.

**To add analytics or reporting:**
- Add computed fields or new models as needed.
- Add new menu items and views in XML.
- Use Odoo's reporting tools or integrate with external BI tools.

---

## Testing

- Write unit tests for model methods and business logic.
- Use Odoo's test framework for integration tests.
- Test frontend flows manually or with Selenium.
- For migrations, use scripts in `upgrade/`.

---

## Troubleshooting

- Check Odoo logs for errors (`odoo.log`).
- Ensure all dependencies are installed and up to date.
- If a field is missing after upgrade, run the upgrade script in `upgrade/`.
- For frontend issues, check browser console and network logs.

---

## Contributing

- Fork the repository and create a feature branch.
- Follow PEP8 and Odoo coding standards.
- Add docstrings and comments for clarity.
- Submit pull requests with a clear description of changes.

---

## License

This module is licensed under LGPL-3. See `__manifest__.py` for details.

---

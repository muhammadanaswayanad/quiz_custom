from . import quiz
from . import question
from . import session  # Import session first to avoid circular import
from . import response
from . import question_extension
from . import question_evaluation  # Add this new module
from . import ghost_models

# Ensure that the new model is added to the models initialization if that's not already done

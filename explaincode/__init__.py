"""
ExplainCode 2.0 package.
A natural language programming environment bridging natural language algorithmic
thinking and conventional Python programming.
"""

__version__ = "2.0.0"

_EXPORTS = {
    "ExplainAICompiler": ".compiler",
    "ExplainAIParser": ".compiler",
    "ExplainCodeCompiler": ".compiler",
    "ExplainCodeParser": ".compiler",
    "ExplainCodeInterpreter": ".interpreter",
    "ExplainCodeApp": ".interpreter",
    "ExplainCodeStepper": ".stepper",
    "StepperState": ".stepper",
    "ConceptExplainer": ".concepts",
    "explain_code": ".concepts",
    "ErrorTutor": ".errors",
    "ErrorReport": ".errors",
    "Challenge": ".challenges",
    "ChallengeValidator": ".challenges",
    "get_all_challenges": ".challenges",
    "get_challenge_by_id": ".challenges",
    "ProgressionTracker": ".progression",
    "TransitionManager": ".transition",
    "TransitionExercise": ".transition",
    "ResearchAnalytics": ".analytics",
}

__all__ = list(_EXPORTS.keys()) + ["__version__"]


def __getattr__(name):
    if name in _EXPORTS:
        import importlib
        mod = importlib.import_module(_EXPORTS[name], __name__)
        val = getattr(mod, name)
        globals()[name] = val
        return val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(__all__)

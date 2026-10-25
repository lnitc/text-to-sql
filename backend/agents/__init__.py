"""Agents package for CrewAI orchestration"""

# The CrewAI implementation is imported lazily: importing crewai takes several
# seconds and the API only uses the simplified pipeline, which shouldn't pay
# that startup cost.


def __getattr__(name):
    if name in ("create_text_to_sql_crew", "TextToSQLCrew"):
        from . import data_crew

        return getattr(data_crew, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["create_text_to_sql_crew", "TextToSQLCrew"]

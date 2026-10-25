"""Agents package: simplified and CrewAI multi-agent Text-to-SQL pipelines"""

# The CrewAI implementation is imported lazily: importing crewai takes several
# seconds, and the default simplified pipeline shouldn't pay that startup cost.


def __getattr__(name):
    if name in ("create_crew_pipeline", "CrewTextToSQLPipeline"):
        from . import data_crew

        return getattr(data_crew, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["create_crew_pipeline", "CrewTextToSQLPipeline"]

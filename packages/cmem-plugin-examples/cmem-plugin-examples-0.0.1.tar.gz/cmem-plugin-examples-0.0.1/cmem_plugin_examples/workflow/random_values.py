"""Random values workflow plugin module"""
import uuid
from secrets import token_urlsafe

from cmem_plugin_base.dataintegration.description import Plugin, PluginParameter
from cmem_plugin_base.dataintegration.entity import (
    Entities,
    Entity,
    EntitySchema,
    EntityPath,
)
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin


@Plugin(
    label="Random Values (Example)",
    description="Generates random values of X rows a Y values.",
    documentation="""
# Generate Random Values

This workflow operator python plugin generates random values.

The values are generated in X rows a Y values. Both parameter can be specified:

- 'number_of_entities': How many rows do you need.
- 'number_of_values': How many values per row do you need.
""",
    parameters=[
        PluginParameter(
            name="number_of_entities",
            label="Number of Entities",
            description="How many rows do you need.",
            default_value="100"
        ),
        PluginParameter(
            name="number_of_values",
            label="Number of Values",
            description="How many values per row do you need.",
            default_value="10"
        )
    ]
)
class RandomValues(WorkflowPlugin):
    """Example Workflow Plugin: Random Values"""

    def __init__(
            self,
            number_of_entities: int,
            number_of_values: int
    ) -> None:
        self.number_of_entities = number_of_entities
        self.number_of_values = number_of_values

    def execute(self, inputs=()) -> Entities:
        entities = []
        for _ in range(self.number_of_entities):
            entity_uri = f"urn:uuid:{str(uuid.uuid4())}"
            values = []
            for _ in range(self.number_of_values):
                values.append([token_urlsafe(16)])
            entities.append(
                Entity(
                    uri=entity_uri,
                    values=values
                )
            )
        paths = []
        for path_no in range(self.number_of_values):
            path_uri = f"https://example.org/vocab/RandomValuePath/{path_no}"
            paths.append(
                EntityPath(
                    path=path_uri
                )
            )
        schema = EntitySchema(
            type_uri="https://example.org/vocab/RandomValueRow",
            paths=paths,
        )
        return Entities(entities=entities, schema=schema)

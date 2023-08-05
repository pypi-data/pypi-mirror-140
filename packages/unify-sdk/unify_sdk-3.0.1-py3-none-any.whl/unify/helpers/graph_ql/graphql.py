from gql_query_builder import GqlQuery

from typing import Dict, List, Union
import json


class GraphQLBuilder:

    @staticmethod
    def build_input_here(self, input: Dict[str, Union[str, int]], initial_str: str):
        inputs: List[str] = []

        final_str = initial_str

        if input != {}:
            key = list(input.keys())[0]
            nested_keys = list()

            while isinstance(input[key], dict):
                nested_keys.append(key)
                input = input[key]
                key = list(input.keys())[0]

            for key, value in input.items():
                if nested_keys:
                    if type(value) is str:
                        inputs.append(f'{key}: "{value}"')  # Nested input won't have double quotes
                    else:
                        inputs.append(f'{key}: {value}')  # Nested input won't have double quotes

                else:
                    inputs.append(f'{key}: {value}')

            final_str += '('

            for key in nested_keys:
                final_str = final_str + key + ': {'

            final_str = final_str + ", ".join(inputs)

            for _ in nested_keys:
                final_str += '}'

            final_str += ')'

        return final_str

    def build_generic_query(
            self,
            query_name=None,
            query_input: dict = None,
            query_alias=None,
            fields: list = None,
            field_alias: str = None,
            operation_type=None,
            operation_name=None,
            operation_queries: list = None,
            operation_input: dict = None,
    ):
        query = GqlQuery()

        operation_params = dict()
        build_oper = False
        if operation_name:
            operation_params["name"] = operation_name
            build_oper = True
        if operation_type:
            operation_params["query_type"] = operation_type
            build_oper = True
        if operation_input:
            operation_params["input"] = operation_input
            build_oper = True
        if operation_queries:
            operation_params["queries"] = operation_queries
            build_oper = True

        if build_oper:
            query = query.operation(**operation_params)

        query_params = dict()
        build_query = False
        if query_alias:
            query_params["alias"] = query_alias
            build_query = True

        if query_name:
            query_params["name"] = query_name
            build_query = True

        if query_input:
            query_params["input"] = query_input
            build_query = True

        if build_query:
            query = query.query(**query_params)

        if fields:
            query.fields(fields=fields)

        return query.generate()

    def build_fragment(self, fields, fragment_name, interface_name):

        return GqlQuery().fields(fields).fragment(fragment_name, interface_name).generate()

    def build_simple_query(self, query_name, query_input: dict = None, query_alias=None, fields: list = None):

        query = GqlQuery()

        query_params = dict()

        if query_alias:
            query_params["alias"] = query_alias

        if query_name:
            query_params["name"] = query_name

        if query_input:
            query_params["input"] = query_input

        if fields:
            query.fields(fields=fields)

        query = query.query(**query_params)

        return query.generate()

    def build_last_updated_fragment(self):
        return self.build_fragment(
            fragment_name="LastUpdatedParts",
            interface_name="Artifact",
            fields=[
                self.build_simple_query(
                    query_name="lastUpdated",
                    fields=[
                        self.build_simple_query(
                            query_name="auditee",
                            fields=[
                                "id",
                                self.build_simple_query(
                                    query_name="details",
                                    fields=[
                                        "name",
                                        "__typename"
                                    ]
                                ),
                                "__typename"
                            ]
                        ),
                        "timestamp",
                        "__typename"
                    ]
                ),
                "__typename"
            ]
        )

    def build_common_parts_fragment(self):
        return self.build_fragment(
            fields=[
                "uuid",
                "name",
                "orgId",
                self.build_simple_query(
                    query_name="id",
                    fields=[
                        "id",
                        "type",
                        "__typename"
                    ]
                ),
                "...LastUpdatedParts",
                "facets",
                "description",
                "__typename",

            ],
            fragment_name="CommonParts",
            interface_name="Artifact"
        )

    def mutation_data_build(self, new_name=None, facets: list = None, description: str = None):

        values = dict()

        if facets:
            values["ean_facets"] = facets

        if description:
            values["ean_description"] = description

        return self.mutation_data_build_by_dict(
            new_name=new_name,
            values=values
        )

    def mutation_data_build_by_dict(self, new_name, values: dict):
        data = dict()

        if new_name:
            data["name"] = new_name

        add = []

        for key, value in values.items():

            add.append(
                {
                    "key": key,
                    "value": json.dumps(value)
                }
            )

        if len(add) > 0:
            data["added"] = add

        return data

    def build_artifact_mutation(self, artifact_id, artifact_type="dataset", data=None):
        """
        This builds the mutation graphql query
        :param artifact_id: pipeline or dataset id to be modified
        :return:
        """

        common_parts = self.build_common_parts_fragment()

        LastUpdatedParts = self.build_last_updated_fragment()

        artifacts = self.build_simple_query(
            query_name="updateArtifact",
            query_input={"id": "$id", "data": "$data"},
            fields=[
                "seqNum",
                self.build_simple_query(
                    query_name="artifact",
                    fields=[
                        "...CommonParts",
                        "__typename"
                    ]
                ),
                "__typename"
            ]
        )

        final = self.build_generic_query(
            operation_name="updateArtifact",
            operation_type="mutation",
            operation_input=
            {
                "$id": "ArtifactIdInput!",
                "$data": "ArtifactInput!"
            },
            operation_queries=[artifacts]
        )

        final_query = "".join(
            [final, common_parts, LastUpdatedParts]
        )

        results = {
            "operationName": "updateArtifact",
            "variables": {
                "id": {
                    "id": artifact_id,
                    "type": artifact_type
                },
                "data": data
            },
            "query": final_query,
        }

        return json.dumps(results)


GqlQuery.build_input = GraphQLBuilder.build_input_here

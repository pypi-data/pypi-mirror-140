import json

from unify.helpers.graph_ql.graphql import GraphQLBuilder


class DatasetGrapql(GraphQLBuilder):

    def mutation_query(self, dataset_id, new_name=None, facets: list = None, description: str = None):

        data = self.mutation_data_build(
            new_name=new_name,
            facets=facets,
            description=description
        )

        query = self.build_artifact_mutation(
            artifact_id=dataset_id,
            data=data,
            artifact_type="dataset"
        )

        return query

    def build_dataset_query(
            self,
            include_schema=True,
            count=True,
            page_num=1,
            page_size=100,
            is_deleted=False,
            facets=None
    ):

        art_count = self.build_generic_query(
            query_name="artifactCount",
            query_input={"pagination": "$pagination"},
        )

        artifacts = self.build_simple_query(
            query_name="artifacts",
            query_input={"pagination": "$pagination"},
            fields=[
                "...CommonParts",
                "... on",
                self.build_simple_query(
                    query_name="Dataset",
                    fields=[
                        "...DatasetParts",
                        "__typename"
                    ]
                ),
                "__typename"
            ]
        )

        common_parts = self.build_common_parts_fragment()

        LastUpdatedParts = self.build_last_updated_fragment()

        fields = [
            "table",
            "numPipelines",
            self.build_simple_query(
                query_name="labels",
                fields=[
                    'raw(fields: ["ean_source_type", "ean_ready", "ean_dataArchiveServerName"])',
                    "__typename"
                ]
            ),
            "__typename"
        ]

        if include_schema:
            fields.append("schema")

        DatasetParts = self.build_fragment(
            fragment_name="DatasetParts",
            interface_name="Dataset",
            fields=fields
        )

        queries = [artifacts]

        if count:
            queries.append(art_count)

        final = self.build_generic_query(
            operation_name="fetchDatasets",
            operation_type="query",
            operation_input={"$pagination": "PaginationInput!"},
            operation_queries=queries
        )

        final_query = "".join(
            [common_parts, LastUpdatedParts, DatasetParts, final]
        )

        filters = 'isDeleted = "{}" && type = "dataset"'.format(is_deleted)

        if facets:
            for facet in facets:
                filters += ' && facets = "{}"'.format(str(facet))

        results = {
            "operationName": "fetchDatasets",
            "query": final_query,
            "variables": {
                "pagination": {
                    "pageInfo": {
                        "pageNum": page_num,
                        "pageSize": page_size
                    },
                    "filter": filters
                }
            }
        }

        return json.dumps(results)

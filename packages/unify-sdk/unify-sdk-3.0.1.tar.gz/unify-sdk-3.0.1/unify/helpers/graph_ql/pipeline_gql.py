import json
from unify.helpers.graph_ql.graphql import GraphQLBuilder


class PipelineGrapql(GraphQLBuilder):

    def get_non_deleted_pipelines(self, pipeline_type="standard"):
        return self.build_pipeline_query(is_deleted=False, pipeline_type=pipeline_type)

    def get_deleted_pipelines(self, pipeline_type="standard"):
        return self.build_pipeline_query(is_deleted=True, pipeline_type=pipeline_type)

    def get_pipelines_query(self, pipeline_type="standard"):
        return self.build_pipeline_query(is_deleted=None, pipeline_type=pipeline_type)

    def get_functions_query(self):
        return self.build_pipeline_query(
            pipeline_type="function"
        )

    def mutation_query(self, pipeline_id, new_name=None, facets: list = None, description: str = None):

        data = self.mutation_data_build(
            new_name=new_name,
            facets=facets,
            description=description
        )

        query = self.build_artifact_mutation(
            artifact_id=pipeline_id,
            data=data,
            artifact_type="pipeline"
        )

        return query

    def build_pipeline_query(
            self,
            count=True,
            page_num: int = 1,
            page_size: int = 100,
            facets=None,
            is_deleted: object = False,
            pipeline_type="standard"
    ):

        if is_deleted not in [False, True, None]:
            raise Exception("is_deleted must be False,True,None")

        artifacts = self.build_simple_query(
            query_name="artifacts",
            query_input={"pagination": "$pagination"},
            fields=[
                "...CommonParts",
                "... on",
                self.build_simple_query(
                    query_name="Pipeline",
                    fields=[
                        "...PipelineParts",
                        "__typename"
                    ]
                ),
                "__typename"
            ]
        )

        common_parts = self.build_common_parts_fragment()

        LastUpdatedParts = self.build_last_updated_fragment()

        filter_relations = 'direction=forward && type=uses && artifact.type=dataset'

        if is_deleted is True:
            filter_relations += " && artifact.isDeleted = true"
        elif is_deleted is False:
            filter_relations += " && artifact.isDeleted = false"

        fields = [
            "legacyId",
            "autosync",
            "pipelineType",
            "columnFunction",
            self.build_simple_query(
                query_name="relationships",
                query_alias="sources",
                fields=[
                    self.build_simple_query(
                        query_name="artifact",
                        fields=[
                            "name",
                            "__typename"
                        ]
                    ),
                    "__typename"
                ],
                query_input={
                    "pagination": {
                        "filter": filter_relations,
                        "pageInfo": {
                            "pageNum": page_num,
                            "pageSize": page_size
                        }
                    }
                }
            )
            ,
            self.build_simple_query(
                query_name="relationships",
                query_alias="sinks",
                fields=[
                    self.build_simple_query(
                        query_name="artifact",
                        fields=[
                            "name",
                            "__typename"
                        ]
                    ),
                    "__typename"
                ],
                query_input={
                    "pagination": {
                        "filter": filter_relations,
                        "pageInfo": {
                            "pageNum": page_num,
                            "pageSize": page_size
                        }
                    }
                }
            ),
            "__typename"
        ]

        DatasetParts = self.build_fragment(
            fragment_name="PipelineParts",
            interface_name="Pipeline",
            fields=fields
        )

        queries = [artifacts]

        if count:
            art_count = self.build_generic_query(
                query_name="artifactCount",
                query_input={"pagination": "$pagination"},
            )
            queries.append(art_count)

        final = self.build_generic_query(
            operation_name="fetchPipelines",
            operation_type="query",
            operation_input={"$pagination": "PaginationInput!"},
            operation_queries=queries
        )

        final_query = ''.join(
            [final, common_parts, LastUpdatedParts, DatasetParts]
        )

        filters = 'type = "pipeline" && pipelineType="{}"'.format(pipeline_type)

        if is_deleted is True:
            filters += ' && isDeleted = "true"'
        elif is_deleted is False:
            filters += ' && isDeleted = "false"'

        if facets:
            for facet in facets:
                filters += ' && facets = "{}"'.format(str(facet))

        results = {
            "operationName": 'fetchPipelines',
            "query": final_query,
            "variables": {
                "pagination": {
                    "filter": filters,
                    "pageInfo": {
                        "pageNum": page_num,
                        "pageSize": page_size
                    }
                }
            }
        }

        return json.dumps(results).replace("'", "")

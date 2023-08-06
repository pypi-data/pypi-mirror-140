from typing import List, Optional, Set
from uuid import uuid4

import networkx as nx
from argo_workflow_tools.models.io.argoproj.workflow import v1alpha1 as argo

from argo_workflow_tools.dsl.workflow import WorkflowTemplate
from argo_workflow_tools.dsl import compile_workflow
from argo_workflow_tools.dsl.node import WorkflowTemplateNode


def build_workflow_dependencies_graph(
        workflow_template: WorkflowTemplateNode,
        all_wf_templates: List[argo.WorkflowTemplate],
) -> nx.DiGraph:
    compiled_workflow = compile_workflow(workflow_template)
    graph_builder = WorkflowTemplateGraphBuilder(all_wf_templates)
    workflow_dependencies_graph = graph_builder.build_workflow_graph(compiled_workflow)
    return workflow_dependencies_graph


class WorkflowTemplateGraphBuilder:
    def __init__(self, all_wf_templates_list: List[argo.WorkflowTemplate]):
        self._all_wf_templates_list = all_wf_templates_list
        self._graph: nx.DiGraph = None

    def build_workflow_graph(self, compiled_workflow):
        self._graph = nx.DiGraph()

        self.add_template_subgraph(compiled_workflow, parent_node_id=None)
        return self._graph

    def add_template_subgraph(self, dsl_wf_template: WorkflowTemplate, parent_node_id: Optional[str]):
        wf_template = dsl_wf_template.to_model()

        curr_node_id = self._create_node_for_wf_template(wf_template, parent_node_id)

        referred_wf_template_names = self._extract_referred_wf_template_names(wf_template)
        for wf_template_name in referred_wf_template_names:
            child_dsl_wf_template = self._find_wf_template_in_templates_list(wf_template_name)
            self.add_template_subgraph(child_dsl_wf_template, parent_node_id=curr_node_id)

    def _create_node_for_wf_template(self, wf_template: argo.WorkflowTemplate, parent_node_id: str) -> str:
        node_id = self._new_node_id()
        wf_template_name = wf_template.metadata.name or wf_template.metadata.generate_name

        self._graph.add_node(node_id, name=wf_template_name)
        if parent_node_id is not None:
            self._graph.add_edge(parent_node_id, node_id)
        return node_id

    def _extract_referred_wf_template_names(self, wf_template) -> Set[str]:
        referred_wf_template_names = set()
        for inner_template in wf_template.spec.templates:
            is_dag_template = inner_template.dag is not None
            is_steps_template = inner_template.steps is not None
            is_leaf_template = inner_template.container is not None or inner_template.script is not None

            if is_dag_template:
                for task in inner_template.dag.tasks:
                    if task.template_ref is not None:
                        referred_wf_template_names.add(task.template_ref.name)

            elif is_steps_template:
                for step in inner_template.steps:
                    if step.template_ref is not None:
                        referred_wf_template_names.add(step.template_ref.name)

            elif is_leaf_template:
                pass

            else:
                raise NotImplementedError(f"unsupported template: {inner_template}")

        return referred_wf_template_names

    def _find_wf_template_in_templates_list(self, wf_template_name) -> WorkflowTemplate:
        matched_wf_templates = list(filter(
            lambda t: t.name == wf_template_name and isinstance(t, WorkflowTemplate),
            self._all_wf_templates_list
        ))
        assert any(matched_wf_templates), \
            f"couldn't find workflow template with the name: '{wf_template_name}' in the workflow templates list"
        assert len(matched_wf_templates) == 1, \
            f"found multiple templates with the name '{wf_template_name}', this is unexpected"
        return matched_wf_templates[0]

    @staticmethod
    def _find_template_by_name(workflow_model: argo.WorkflowTemplate, template_name: str) -> argo.Template:
        found_template = next(filter(lambda t: t.name == template_name, workflow_model.spec.templates))
        return found_template

    @staticmethod
    def _new_node_id():
        return uuid4().hex

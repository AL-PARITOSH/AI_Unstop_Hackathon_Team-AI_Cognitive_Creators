from app.models.request import VisualRequest
from app.models.specs.base import BaseVisualSpec
from app.models.specs.diagram import DiagramSpec, DiagramElement, DiagramConnection, DiagramAnnotation
from app.models.specs.flowchart import FlowchartSpec, FlowNode, FlowEdge
from app.models.specs.graph import GraphSpec, GraphSeries, GraphPointAnnotation
from app.models.specs.formula import FormulaSpec, FormulaVariable, FormulaStep
from app.models.specs.timeline import TimelineSpec, TimelineEvent
from app.models.specs.code_execution import CodeExecutionSpec, ExecutionTraceStep
from app.models.specs.architecture import ArchitectureSpec, ArchLayer, ArchComponent, ArchConnection

class DynamicSpecBuilder:
    """
    Algorithmic fallback specification builder that generates structured,
    subject-aware specifications for novel or arbitrary educational concepts.
    """

    @staticmethod
    def build(request: VisualRequest, visual_type: str) -> BaseVisualSpec:
        concept = request.concept.strip()
        topic = request.topic.strip()
        context = request.lesson_context or f"Educational breakdown of {concept} in {topic}."

        if visual_type == "formula":
            return DynamicSpecBuilder._build_formula(concept, topic, context)
        elif visual_type == "graph":
            return DynamicSpecBuilder._build_graph(concept, topic, context)
        elif visual_type == "flowchart":
            return DynamicSpecBuilder._build_flowchart(concept, topic, context)
        elif visual_type == "code_execution":
            return DynamicSpecBuilder._build_code(concept, topic, context)
        elif visual_type == "timeline":
            return DynamicSpecBuilder._build_timeline(concept, topic, context)
        elif visual_type == "architecture":
            return DynamicSpecBuilder._build_architecture(concept, topic, context)
        else:
            return DynamicSpecBuilder._build_diagram(concept, topic, context)

    @staticmethod
    def _build_diagram(concept: str, topic: str, context: str) -> DiagramSpec:
        return DiagramSpec(
            title=f"{concept} Structural Breakdown",
            explanation=f"Conceptual breakdown and component interaction diagram for {concept} in {topic}.",
            canvas_width=800,
            canvas_height=420,
            elements=[
                DiagramElement(id="core", label=concept, subtext=f"Core Concept ({topic})", shape="box", x=300, y=160, width=200, height=90, color="#1E293B", bg_color="#EFF6FF", border_color="#3B82F6"),
                DiagramElement(id="input", label="Inputs & Preconditions", subtext="Foundational Requirements", shape="pill", x=50, y=175, width=190, height=60, color="#059669", bg_color="#D1FAE5", border_color="#10B981"),
                DiagramElement(id="output", label="Outcomes & Applications", subtext="Target Results", shape="pill", x=560, y=175, width=190, height=60, color="#D97706", bg_color="#FEF3C7", border_color="#F59E0B"),
                DiagramElement(id="rules", label="Governing Principles", subtext="Key Mechanisms", shape="card", x=300, y=40, width=200, height=70, color="#7C3AED", bg_color="#EDE9FE", border_color="#8B5CF6")
            ],
            connections=[
                DiagramConnection(source_id="input", target_id="core", label="Feeds into", arrow_type="forward", color="#059669"),
                DiagramConnection(source_id="core", target_id="output", label="Produces", arrow_type="forward", color="#2563EB"),
                DiagramConnection(source_id="rules", target_id="core", label="Governs", arrow_type="dashed", color="#7C3AED")
            ],
            annotations=[
                DiagramAnnotation(title="Summary", text=context[:120], x=40, y=340, color="#2563EB")
            ]
        )

    @staticmethod
    def _build_flowchart(concept: str, topic: str, context: str) -> FlowchartSpec:
        return FlowchartSpec(
            title=f"{concept} Step-by-Step Flowchart",
            explanation=f"Logical procedure and operational decision path for {concept}.",
            orientation="vertical",
            nodes=[
                FlowNode(id="f1", label=f"Start: Initiate {concept}", node_type="start", detail="Initial state and inputs"),
                FlowNode(id="f2", label="Analyze Parameters & Conditions", node_type="process", detail="Evaluate state against requirements"),
                FlowNode(id="f3", label="Are Requirements Satisfied?", node_type="decision", detail="Decision check"),
                FlowNode(id="f4", label="Execute Core Transformation", node_type="process", detail="Main algorithmic / physical process"),
                FlowNode(id="f5", label="Adjust & Retry Parameters", node_type="process", detail="Remediation loop"),
                FlowNode(id="f6", label=f"Complete: {concept} Finalized", node_type="end", detail="Desired final outcome reached")
            ],
            edges=[
                FlowEdge(source_id="f1", target_id="f2", label="Begin"),
                FlowEdge(source_id="f2", target_id="f3", label="Check criteria"),
                FlowEdge(source_id="f3", target_id="f4", condition="Yes", label="Valid"),
                FlowEdge(source_id="f3", target_id="f5", condition="No", label="Invalid"),
                FlowEdge(source_id="f5", target_id="f2", label="Retry"),
                FlowEdge(source_id="f4", target_id="f6", label="Success")
            ]
        )

    @staticmethod
    def _build_formula(concept: str, topic: str, context: str) -> FormulaSpec:
        return FormulaSpec(
            title=f"Mathematical Formulation: {concept}",
            explanation=f"Algebraic relationships and variable derivations governing {concept}.",
            latex=r"y = f(x_1, x_2, \dots, x_n)",
            display_latex=r"R = \sum_{i=1}^{n} w_i \cdot x_i \quad \Longleftrightarrow \quad \Delta R = rac{\partial f}{\partial x} \cdot \Delta x",
            variables=[
                FormulaVariable(symbol="R", name="Resultant / Output", unit="Standard Units", description="The primary dependent variable"),
                FormulaVariable(symbol="x_i", name="Input Parameter i", unit="Variable Units", description="Independent factor contributing to system state"),
                FormulaVariable(symbol="w_i", name="Weight / Constant Coefficient", unit="Dimensionless / Scaling", description="Proportionality constant")
            ],
            derivation_steps=[
                FormulaStep(step_number=1, title="Identify Governing Law", latex_expression=r"R = f(X)", explanation=f"Express fundamental dependency of {concept}."),
                FormulaStep(step_number=2, title="Apply Boundary Conditions", latex_expression=r"\lim_{x 	o x_0} f(x) = L", explanation="Determine steady-state response under initial conditions."),
                FormulaStep(step_number=3, title="Solve for Target Parameter", latex_expression=r"x_1 = g(R, x_2, \dots)", explanation="Isolate specific variable for direct calculation.")
            ],
            example_calculation=f"Applying standard parameter values for {concept} yields verified output values."
        )

    @staticmethod
    def _build_graph(concept: str, topic: str, context: str) -> GraphSpec:
        x_vals = [float(i) for i in range(-5, 6)]
        y_vals = [float(x ** 2) for x in x_vals]
        return GraphSpec(
            title=f"{concept} Analytical Trend Plot",
            explanation=f"Coordinate relationship and trend curve for {concept}.",
            chart_type="function_plot",
            x_label="Independent Variable (X)",
            y_label="Response Value (Y)",
            series=[
                GraphSeries(name=concept, x_values=x_vals, y_values=y_vals, mode="lines+markers", line_color="#2563EB", line_width=3)
            ],
            annotations=[
                GraphPointAnnotation(x=0.0, y=0.0, text="Equilibrium Point (0, 0)", point_color="#10B981")
            ]
        )

    @staticmethod
    def _build_timeline(concept: str, topic: str, context: str) -> TimelineSpec:
        return TimelineSpec(
            title=f"{concept} Historical Chronology",
            explanation=f"Chronological sequence of evolutionary events defining {concept}.",
            start_date="Phase 1",
            end_date="Modern Era",
            events=[
                TimelineEvent(date_or_period="Early Phase", title="Foundational Origins", description=f"Initial discovery and theoretical formulation of {concept}.", category="Inception", importance="high"),
                TimelineEvent(date_or_period="Middle Phase", title="Rapid Development & Expansion", description="Crucial breakthroughs, validation experiments, and widespread adoption.", category="Advancement", importance="high"),
                TimelineEvent(date_or_period="Contemporary Era", title="Modern Standardization", description="Integration into modern scientific and technological curricula.", category="Modern", importance="medium")
            ]
        )

    @staticmethod
    def _build_architecture(concept: str, topic: str, context: str) -> ArchitectureSpec:
        return ArchitectureSpec(
            title=f"{concept} System Architecture",
            explanation=f"Modular system layers and data communication channels for {concept}.",
            layers=[
                ArchLayer(id="l1", name="1. Client / Ingestion Layer", description="Entrypoint & Interface", color="#2563EB"),
                ArchLayer(id="l2", name="2. Processing & Core Logic", description="Transformation Engine", color="#7C3AED"),
                ArchLayer(id="l3", name="3. Storage & Output Layer", description="Persistence & Results", color="#059669")
            ],
            components=[
                ArchComponent(id="c1", name="API Gateway / Interface", layer_id="l1", technology="REST / WebSocket", role="Handles requests", icon="server"),
                ArchComponent(id="c2", name=f"{concept} Core Engine", layer_id="l2", technology="Python / Compute Engine", role="Processes data", icon="cpu"),
                ArchComponent(id="c3", name="Database / State Store", layer_id="l3", technology="Storage Engine", role="Persists state", icon="database")
            ],
            connections=[
                ArchConnection(from_id="c1", to_id="c2", label="Payload", protocol_or_type="sync"),
                ArchConnection(from_id="c2", to_id="c3", label="Save Output", protocol_or_type="pipeline")
            ],
            key_principles=[
                "Decoupled modular architecture.",
                "Horizontally scalable compute components."
            ]
        )

    @staticmethod
    def _build_code(concept: str, topic: str, context: str) -> CodeExecutionSpec:
        code_lines = [
            f"# Implementation of {concept}",
            "def execute_concept(data_input):",
            "    results = []",
            "    for item in data_input:",
            "        processed = item * 2",
            "        results.append(processed)",
            "    return results",
            "",
            "# Test run",
            "sample_data = [1, 2, 3, 4]",
            "output = execute_concept(sample_data)",
            "print(f'Result: {output}')"
        ]
        sample_code = "\n".join(code_lines)
        return CodeExecutionSpec(
            title=f"{concept} Code Implementation & Trace",
            explanation=f"Algorithmic execution trace and memory walkthrough for {concept}.",
            language="python",
            code=sample_code,
            highlighted_lines=[4, 5, 6],
            execution_trace=[
                ExecutionTraceStep(step_number=1, line_number=1, code_line="def execute_concept(data_input):", explanation="Define processing routine", variables_state={"data_input": [1, 2, 3, 4]}),
                ExecutionTraceStep(step_number=2, line_number=3, code_line="results = []", explanation="Initialize accumulator list", variables_state={"results": []}),
                ExecutionTraceStep(step_number=3, line_number=4, code_line="for item in data_input: (item = 1)", explanation="Process first element", variables_state={"item": 1, "processed": 2, "results": [2]}),
                ExecutionTraceStep(step_number=4, line_number=7, code_line="return results", explanation="Return completed output array", variables_state={"results": [2, 4, 6, 8]}, output_printed="Result: [2, 4, 6, 8]")
            ],
            expected_output="Result: [2, 4, 6, 8]",
            key_takeaways=[
                "Linear O(N) iteration over input items.",
                "Pure functional transformation without side-effects."
            ]
        )

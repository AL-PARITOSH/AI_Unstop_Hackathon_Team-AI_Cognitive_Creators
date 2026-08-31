from typing import Optional, Dict
from app.models.specs.formula import FormulaSpec, FormulaVariable, FormulaStep
from app.models.specs.diagram import DiagramSpec, DiagramElement, DiagramConnection, DiagramAnnotation
from app.models.specs.flowchart import FlowchartSpec, FlowNode, FlowEdge
from app.models.specs.graph import GraphSpec, GraphSeries, GraphPointAnnotation
from app.models.specs.timeline import TimelineSpec, TimelineEvent
from app.models.specs.code_execution import CodeExecutionSpec, ExecutionTraceStep
from app.models.specs.architecture import ArchitectureSpec, ArchLayer, ArchComponent, ArchConnection
from app.models.specs.base import BaseVisualSpec

class CurriculumKnowledgeBase:
    @staticmethod
    def get_newtons_second_law(visual_type: str = "formula") -> BaseVisualSpec:
        if visual_type == "formula":
            return FormulaSpec(
                title="Newton's Second Law of Motion",
                explanation="Newton's second law quantifies the relationship between net force, mass, and acceleration (F = m · a).",
                latex=r"F = m \cdot a",
                display_latex=r"F_{\text{net}} = m \cdot a \quad \Longleftrightarrow \quad a = \frac{F_{\text{net}}}{m}",
                variables=[
                    FormulaVariable(symbol="F", name="Net Force", unit="Newtons (N)", description="Vector sum of external forces"),
                    FormulaVariable(symbol="m", name="Mass", unit="Kilograms (kg)", description="Quantitative measure of inertia"),
                    FormulaVariable(symbol="a", name="Acceleration", unit="m/s²", description="Rate of change of velocity")
                ],
                derivation_steps=[
                    FormulaStep(step_number=1, title="State Law", latex_expression=r"F = \frac{dp}{dt}", explanation="Time rate of change of momentum."),
                    FormulaStep(step_number=2, title="Constant Mass", latex_expression=r"F = m \cdot a", explanation="Assuming constant mass.")
                ],
                example_calculation="For mass m = 10 kg and force F = 50 N: a = F / m = 50 / 10 = 5 m/s²."
            )
        else:
            return DiagramSpec(
                title="Newton's Second Law Force & Acceleration Diagram",
                explanation="Visualizing force vector acting upon a mass block.",
                canvas_width=800,
                canvas_height=400,
                elements=[
                    DiagramElement(id="block", label="Mass (m = 10 kg)", subtext="Body", shape="box", x=300, y=160, width=200, height=90, color="#1E293B", bg_color="#E2E8F0", border_color="#475569"),
                    DiagramElement(id="f_app", label="Force (F = 50 N)", subtext="Vector →", shape="pill", x=540, y=180, width=180, height=50, color="#2563EB", bg_color="#DBEAFE", border_color="#3B82F6"),
                    DiagramElement(id="accel", label="Acceleration (a = 5 m/s²)", subtext="Result →", shape="pill", x=300, y=60, width=200, height=50, color="#059669", bg_color="#D1FAE5", border_color="#10B981")
                ],
                connections=[
                    DiagramConnection(source_id="block", target_id="f_app", label="Applied Force", arrow_type="forward", color="#2563EB"),
                    DiagramConnection(source_id="block", target_id="accel", label="Accelerates", arrow_type="forward", color="#059669")
                ],
                annotations=[
                    DiagramAnnotation(title="Newton's 2nd Law", text="F = m · a: Force directly creates acceleration.", x=40, y=40, color="#2563EB")
                ]
            )

    @staticmethod
    def get_ohms_law(visual_type: str = "formula") -> BaseVisualSpec:
        if visual_type == "formula":
            return FormulaSpec(
                title="Ohm's Law (V = I · R)",
                explanation="Current is directly proportional to voltage and inversely proportional to resistance.",
                latex=r"V = I \cdot R",
                display_latex=r"V = I \cdot R \quad \Longleftrightarrow \quad I = \frac{V}{R} \quad \Longleftrightarrow \quad R = \frac{V}{I}",
                variables=[
                    FormulaVariable(symbol="V", name="Voltage", unit="Volts (V)", description="Electric potential difference"),
                    FormulaVariable(symbol="I", name="Current", unit="Amperes (A)", description="Rate of electric charge flow"),
                    FormulaVariable(symbol="R", name="Resistance", unit="Ohms (Ω)", description="Opposition to current flow")
                ],
                derivation_steps=[
                    FormulaStep(step_number=1, title="Proportionality", latex_expression=r"I \propto V", explanation="Current is proportional to voltage."),
                    FormulaStep(step_number=2, title="Equation Form", latex_expression=r"V = I \cdot R", explanation="Introduce resistance R.")
                ],
                example_calculation="For V = 12V and R = 4Ω: I = V / R = 12 / 4 = 3 Amperes."
            )
        else:
            return DiagramSpec(
                title="Ohm's Law DC Circuit & Triangle",
                explanation="Schematic of a simple closed DC circuit with voltage source, current loop, and resistor.",
                canvas_width=800,
                canvas_height=400,
                elements=[
                    DiagramElement(id="battery", label="DC Voltage (V = 12V)", subtext="Battery", shape="cylinder", x=80, y=150, width=170, height=90, color="#DC2626", bg_color="#FEE2E2", border_color="#EF4444"),
                    DiagramElement(id="current", label="Current (I = 3A)", subtext="Flow", shape="pill", x=315, y=60, width=170, height=50, color="#2563EB", bg_color="#DBEAFE", border_color="#3B82F6"),
                    DiagramElement(id="resistor", label="Resistor (R = 4Ω)", subtext="Load", shape="box", x=550, y=150, width=170, height=90, color="#059669", bg_color="#D1FAE5", border_color="#10B981"),
                    DiagramElement(id="ground", label="Return Path", subtext="0V Reference", shape="pill", x=315, y=280, width=170, height=50, color="#475569", bg_color="#F1F5F9", border_color="#64748B")
                ],
                connections=[
                    DiagramConnection(source_id="battery", target_id="current", label="Current Out", arrow_type="forward", color="#DC2626"),
                    DiagramConnection(source_id="current", target_id="resistor", label="Enters Load", arrow_type="forward", color="#2563EB"),
                    DiagramConnection(source_id="resistor", target_id="ground", label="Voltage Drop", arrow_type="forward", color="#059669"),
                    DiagramConnection(source_id="ground", target_id="battery", label="Closed Loop", arrow_type="forward", color="#475569")
                ],
                annotations=[
                    DiagramAnnotation(title="Ohm's Triangle", text="Cover V: I ? R | Cover I: V / R | Cover R: V / I", x=40, y=30, color="#7C3AED")
                ]
            )

    @staticmethod
    def get_photosynthesis(visual_type: str = "diagram") -> BaseVisualSpec:
        if visual_type == "diagram":
            return DiagramSpec(
                title="Photosynthesis: Chloroplast Anatomy and Reactant Cycles",
                explanation="Photosynthesis converts solar energy, water, and CO2 into glucose and oxygen in plant chloroplasts.",
                canvas_width=800,
                canvas_height=420,
                elements=[
                    DiagramElement(id="sunlight", label="Sunlight (Photons)", subtext="Energy", shape="circle", x=60, y=50, width=120, height=120, color="#D97706", bg_color="#FEF3C7", border_color="#F59E0B"),
                    DiagramElement(id="water", label="Water (6 H2O)", subtext="From Roots", shape="pill", x=60, y=210, width=150, height=55, color="#0284C7", bg_color="#E0F2FE", border_color="#38BDF8"),
                    DiagramElement(id="thylakoid", label="Thylakoid (Light Reactions)", subtext="Chlorophyll", shape="card", x=260, y=100, width=220, height=100, color="#15803D", bg_color="#DCFCE7", border_color="#22C55E"),
                    DiagramElement(id="oxygen", label="Oxygen (6 O2)", subtext="Byproduct", shape="pill", x=260, y=290, width=180, height=50, color="#0D9488", bg_color="#CCFBF1", border_color="#14B8A6"),
                    DiagramElement(id="co2", label="CO2 (6 Carbon Dioxide)", subtext="Stomata", shape="pill", x=550, y=50, width=190, height=55, color="#64748B", bg_color="#F1F5F9", border_color="#94A3B8"),
                    DiagramElement(id="stroma", label="Stroma (Calvin Cycle)", subtext="Sugar Synthesis", shape="card", x=530, y=150, width=220, height=100, color="#166534", bg_color="#BBF7D0", border_color="#16A34A"),
                    DiagramElement(id="glucose", label="Glucose (C6H12O6)", subtext="Sugar Output", shape="pill", x=530, y=300, width=210, height=55, color="#EA580C", bg_color="#FFEDD5", border_color="#FB923C")
                ],
                connections=[
                    DiagramConnection(source_id="sunlight", target_id="thylakoid", label="Light Absorption", arrow_type="forward", color="#F59E0B"),
                    DiagramConnection(source_id="water", target_id="thylakoid", label="Photolysis", arrow_type="forward", color="#0284C7"),
                    DiagramConnection(source_id="thylakoid", target_id="oxygen", label="O2 Release", arrow_type="forward", color="#0D9488"),
                    DiagramConnection(source_id="thylakoid", target_id="stroma", label="ATP + NADPH", arrow_type="forward", color="#15803D"),
                    DiagramConnection(source_id="co2", target_id="stroma", label="Carbon Fixation", arrow_type="forward", color="#64748B"),
                    DiagramConnection(source_id="stroma", target_id="glucose", label="Synthesized Sugar", arrow_type="forward", color="#EA580C")
                ],
                annotations=[
                    DiagramAnnotation(title="Net Equation", text="6CO2 + 6H2O + Light -> C6H12O6 + 6O2", x=40, y=370, color="#166534")
                ]
            )
        else:
            return FlowchartSpec(
                title="Photosynthesis Biochemical Reaction Flowchart",
                explanation="Two-stage photosynthetic reaction cascade.",
                orientation="vertical",
                nodes=[
                    FlowNode(id="p1", label="Light & Water Absorption", node_type="start", detail="Photons absorbed by Photosystem II"),
                    FlowNode(id="p2", label="Photolysis of Water", node_type="process", detail="2H₂O → 4 H⁺ + 4 e⁻ + O₂ released"),
                    FlowNode(id="p3", label="Electron Transport Chain", node_type="process", detail="Generates ATP and NADPH"),
                    FlowNode(id="p4", label="Calvin Cycle Carbon Fixation", node_type="process", detail="CO2 fixed via RuBisCO in stroma"),
                    FlowNode(id="p5", label="Glucose Output & Energy Storage", node_type="end", detail="Produces Glucose (C6H12O6)")
                ],
                edges=[
                    FlowEdge(source_id="p1", target_id="p2", label="Photons initiate"),
                    FlowEdge(source_id="p2", target_id="p3", label="Electrons transfer"),
                    FlowEdge(source_id="p3", target_id="p4", label="ATP + NADPH"),
                    FlowEdge(source_id="p4", target_id="p5", label="Sugar synthesis")
                ]
            )

    @staticmethod
    def get_binary_search(visual_type: str = "flowchart") -> BaseVisualSpec:
        if visual_type == "flowchart":
            return FlowchartSpec(
                title="Binary Search Algorithm Flowchart",
                explanation="Binary Search on sorted array in O(log n) time.",
                orientation="vertical",
                nodes=[
                    FlowNode(id="n1", label="Start: Sorted Array & Target", node_type="start", detail="low = 0, high = len(arr) - 1"),
                    FlowNode(id="n2", label="Is low ≤ high ?", node_type="decision", detail="Check search space exists"),
                    FlowNode(id="n3", label="Calculate mid = (low + high) // 2", node_type="process", detail="Midpoint index calculation"),
                    FlowNode(id="n4", label="Is arr[mid] == Target ?", node_type="decision", detail="Target match check"),
                    FlowNode(id="n5", label="Return mid (Found!)", node_type="end", detail="Success"),
                    FlowNode(id="n6", label="Is arr[mid] < Target ?", node_type="decision", detail="Branch direction"),
                    FlowNode(id="n7", label="low = mid + 1 (Right)", node_type="process", detail="Search right half"),
                    FlowNode(id="n8", label="high = mid - 1 (Left)", node_type="process", detail="Search left half"),
                    FlowNode(id="n9", label="Return -1 (Not Found)", node_type="end", detail="Exhausted")
                ],
                edges=[
                    FlowEdge(source_id="n1", target_id="n2", label="Begin"),
                    FlowEdge(source_id="n2", target_id="n3", condition="Yes", label="True"),
                    FlowEdge(source_id="n2", target_id="n9", condition="No", label="False"),
                    FlowEdge(source_id="n3", target_id="n4", label="Check element"),
                    FlowEdge(source_id="n4", target_id="n5", condition="Yes", label="Match"),
                    FlowEdge(source_id="n4", target_id="n6", condition="No", label="No match"),
                    FlowEdge(source_id="n6", target_id="n7", condition="Yes", label="< Target"),
                    FlowEdge(source_id="n6", target_id="n8", condition="No", label="> Target"),
                    FlowEdge(source_id="n7", target_id="n2", label="Loop back"),
                    FlowEdge(source_id="n8", target_id="n2", label="Loop back")
                ]
            )
        else:
            code_text = "def binary_search(arr, target):\n    low = 0\n    high = len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1\n\nres = binary_search([2, 5, 8, 12, 16, 23, 38, 56, 72, 91], 23)\n"
            return CodeExecutionSpec(
                title="Binary Search Python Execution Trace",
                explanation="Step-by-step memory pointer trace searching for target = 23.",
                language="python",
                code=code_text,
                highlighted_lines=[3, 4, 5, 6, 7, 8],
                execution_trace=[
                    ExecutionTraceStep(step_number=1, line_number=2, code_line="low = 0, high = 9", explanation="Initialize search bounds", variables_state={"low": 0, "high": 9, "target": 23}),
                    ExecutionTraceStep(step_number=2, line_number=4, code_line="mid = (0 + 9) // 2 -> 4", explanation="Mid index 4 has value 16", variables_state={"low": 0, "high": 9, "mid": 4, "arr[mid]": 16}),
                    ExecutionTraceStep(step_number=3, line_number=8, code_line="low = mid + 1 -> 5", explanation="16 < 23, search right half", variables_state={"low": 5, "high": 9, "mid": 4}),
                    ExecutionTraceStep(step_number=4, line_number=4, code_line="mid = (5 + 9) // 2 -> 7", explanation="Mid index 7 has value 56", variables_state={"low": 5, "high": 9, "mid": 7, "arr[mid]": 56}),
                    ExecutionTraceStep(step_number=5, line_number=10, code_line="high = mid - 1 -> 6", explanation="56 > 23, search left half", variables_state={"low": 5, "high": 6, "mid": 7}),
                    ExecutionTraceStep(step_number=6, line_number=4, code_line="mid = (5 + 6) // 2 -> 5", explanation="Mid index 5 has value 23", variables_state={"low": 5, "high": 6, "mid": 5, "arr[mid]": 23}),
                    ExecutionTraceStep(step_number=7, line_number=6, code_line="return 5", explanation="Match found at index 5", variables_state={"result": 5})
                ],
                expected_output="5",
                key_takeaways=[
                    "O(log n) time complexity by halving space.",
                    "Input array must be sorted."
                ]
            )

    @staticmethod
    def get_python_for_loop(visual_type: str = "code_execution") -> BaseVisualSpec:
        if visual_type == "code_execution":
            code_text = 'fruits = ["apple", "banana", "cherry"]\ntotal = 0\n\nfor item in fruits:\n    count = len(item)\n    total += count\n    print(f"{item}: {count}")\n\nprint(f"Total: {total}")\n'
            return CodeExecutionSpec(
                title="Python For Loop Execution & Trace",
                explanation="Sequential iteration over elements of a list in Python.",
                language="python",
                code=code_text,
                highlighted_lines=[4, 5, 6, 7],
                execution_trace=[
                    ExecutionTraceStep(step_number=1, line_number=1, code_line='fruits = ["apple", "banana", "cherry"]', explanation="Instantiate list", variables_state={"fruits": ["apple", "banana", "cherry"], "total": 0}),
                    ExecutionTraceStep(step_number=2, line_number=4, code_line='for item in fruits: (1st item)', explanation="item becomes 'apple'", variables_state={"item": "apple", "total": 0}),
                    ExecutionTraceStep(step_number=3, line_number=6, code_line='total += 5 -> 5', explanation="Add apple length 5", variables_state={"total": 5}, output_printed="apple: 5"),
                    ExecutionTraceStep(step_number=4, line_number=4, code_line='for item in fruits: (2nd item)', explanation="item becomes 'banana'", variables_state={"item": "banana", "total": 5}),
                    ExecutionTraceStep(step_number=5, line_number=6, code_line='total += 6 -> 11', explanation="Add banana length 6", variables_state={"total": 11}, output_printed="banana: 6"),
                    ExecutionTraceStep(step_number=6, line_number=4, code_line='for item in fruits: (3rd item)', explanation="item becomes 'cherry'", variables_state={"item": "cherry", "total": 11}),
                    ExecutionTraceStep(step_number=7, line_number=6, code_line='total += 6 -> 17', explanation="Add cherry length 6", variables_state={"total": 17}, output_printed="cherry: 6"),
                    ExecutionTraceStep(step_number=8, line_number=9, code_line='print(f"Total: {total}")', explanation="Loop finished", variables_state={"total": 17}, output_printed="Total: 17")
                ],
                expected_output="apple: 5\nbanana: 6\ncherry: 6\nTotal: 17",
                key_takeaways=[
                    "Executes block once per element in sequence.",
                    "Variables inside loop mutate state across iterations."
                ]
            )
        else:
            return FlowchartSpec(
                title="Python For Loop Control Flow",
                explanation="Iteration sequence and termination condition of Python loops.",
                orientation="vertical",
                nodes=[
                    FlowNode(id="s1", label="Obtain Iterator from Iterable", node_type="start", detail="iter(fruits)"),
                    FlowNode(id="s2", label="More items in sequence?", node_type="decision", detail="next(iterator)"),
                    FlowNode(id="s3", label="Assign item = next_val", node_type="process", detail="Bind loop variable"),
                    FlowNode(id="s4", label="Execute Loop Body Block", node_type="process", detail="count = len(item); total += count"),
                    FlowNode(id="s5", label="Loop Finished (StopIteration)", node_type="end", detail="Continue past loop")
                ],
                edges=[
                    FlowEdge(source_id="s1", target_id="s2", label="Start"),
                    FlowEdge(source_id="s2", target_id="s3", condition="Yes", label="Item exists"),
                    FlowEdge(source_id="s2", target_id="s5", condition="No", label="Exhausted"),
                    FlowEdge(source_id="s3", target_id="s4", label="Execute"),
                    FlowEdge(source_id="s4", target_id="s2", label="Next")
                ]
            )

    @staticmethod
    def get_ml_pipeline(visual_type: str = "architecture") -> BaseVisualSpec:
        if visual_type == "architecture":
            return ArchitectureSpec(
                title="Machine Learning Pipeline Architecture",
                explanation="End-to-end production ML pipeline from ingestion to serving and monitoring.",
                layers=[
                    ArchLayer(id="l1", name="1. Data Ingestion & Storage", description="Raw streaming & batch", color="#2563EB"),
                    ArchLayer(id="l2", name="2. Feature Engineering", description="Transformation & validation", color="#059669"),
                    ArchLayer(id="l3", name="3. Model Training & Tuning", description="GPU clusters & hyperparams", color="#7C3AED"),
                    ArchLayer(id="l4", name="4. Evaluation & Registry", description="Quality gate & versioning", color="#D97706"),
                    ArchLayer(id="l5", name="5. Serving & Monitoring", description="Inference API & drift monitor", color="#DC2626")
                ],
                components=[
                    ArchComponent(id="c1", name="Data Sources", layer_id="l1", technology="Kafka / S3", role="Ingest event logs", icon="database"),
                    ArchComponent(id="c2", name="Feature Store", layer_id="l2", technology="Feast / Spark", role="Transform vectors", icon="table"),
                    ArchComponent(id="c3", name="Training Cluster", layer_id="l3", technology="PyTorch / GPUs", role="Train weights", icon="cpu"),
                    ArchComponent(id="c4", name="Model Registry", layer_id="l4", technology="MLflow / W&B", role="Version models", icon="archive"),
                    ArchComponent(id="c5", name="Inference Service", layer_id="l5", technology="FastAPI / Triton", role="REST predictions", icon="server"),
                    ArchComponent(id="c6", name="Drift Monitor", layer_id="l5", technology="Prometheus", role="Detect data drift", icon="activity")
                ],
                connections=[
                    ArchConnection(from_id="c1", to_id="c2", label="ETL", protocol_or_type="pipeline"),
                    ArchConnection(from_id="c2", to_id="c3", label="Features", protocol_or_type="stream"),
                    ArchConnection(from_id="c3", to_id="c4", label="Model Artifact", protocol_or_type="sync"),
                    ArchConnection(from_id="c4", to_id="c5", label="Deploy Approved", protocol_or_type="pipeline"),
                    ArchConnection(from_id="c5", to_id="c6", label="Logs", protocol_or_type="stream"),
                    ArchConnection(from_id="c6", to_id="c3", label="Retrain Trigger", protocol_or_type="async")
                ],
                key_principles=[
                    "Reproducibility: Lineage tracked from features to weights.",
                    "Continuous Training: Automated triggers upon data drift.",
                    "Low Latency Serving: Cached feature vectors for sub-ms inference."
                ]
            )
        else:
            return FlowchartSpec(
                title="ML Model Training & Deployment Workflow",
                explanation="Operational workflow and retraining feedback cycle.",
                orientation="vertical",
                nodes=[
                    FlowNode(id="m1", label="Data Validation", node_type="start", detail="Verify feature schemas"),
                    FlowNode(id="m2", label="Train Model Weights", node_type="process", detail="Fit deep learning models on GPU"),
                    FlowNode(id="m3", label="Validation Metric >= Target?", node_type="decision", detail="Quality gate check"),
                    FlowNode(id="m4", label="Deploy to Production", node_type="process", detail="Push container to cluster"),
                    FlowNode(id="m5", label="Adjust Hyperparameters", node_type="process", detail="Tuning feedback"),
                    FlowNode(id="m6", label="Monitor Drift Alert?", node_type="decision", detail="Detect statistical shift"),
                    FlowNode(id="m7", label="Healthy Serving", node_type="end", detail="High SLA inference")
                ],
                edges=[
                    FlowEdge(source_id="m1", target_id="m2", label="Clean features"),
                    FlowEdge(source_id="m2", target_id="m3", label="Trained weights"),
                    FlowEdge(source_id="m3", target_id="m4", condition="Yes", label="Passed"),
                    FlowEdge(source_id="m3", target_id="m5", condition="No", label="Failed"),
                    FlowEdge(source_id="m5", target_id="m2", label="Retrain"),
                    FlowEdge(source_id="m4", target_id="m6", label="Traffic"),
                    FlowEdge(source_id="m6", target_id="m1", condition="Yes", label="Drift -> Retrain"),
                    FlowEdge(source_id="m6", target_id="m7", condition="No", label="Normal")
                ]
            )

    @staticmethod
    def get_french_revolution(visual_type: str = "timeline") -> BaseVisualSpec:
        if visual_type == "timeline":
            return TimelineSpec(
                title="The French Revolution: Key Historical Milestones (1789-1799)",
                explanation="Chronological timeline tracking major phases of the French Revolution.",
                start_date="1789",
                end_date="1799",
                events=[
                    TimelineEvent(date_or_period="May 5, 1789", title="Estates-General Convenes", description="King Louis XVI summons the three estates to resolve debt crisis.", category="Political", importance="high", tags=["Versailles"]),
                    TimelineEvent(date_or_period="June 20, 1789", title="Tennis Court Oath", description="Third Estate vows to establish written constitution.", category="Constitutional", importance="high", tags=["National Assembly"]),
                    TimelineEvent(date_or_period="July 14, 1789", title="Storming of the Bastille", description="Citizens seize the medieval fortress, launching revolution.", category="Uprising", importance="high", tags=["Bastille"]),
                    TimelineEvent(date_or_period="August 26, 1789", title="Declaration of Rights of Man", description="National Assembly proclaims liberty, equality, fraternity.", category="Human Rights", importance="high", tags=["Rights"]),
                    TimelineEvent(date_or_period="September 21, 1792", title="First French Republic Declared", description="Monarchy formally abolished.", category="Political", importance="high", tags=["Republic"]),
                    TimelineEvent(date_or_period="January 21, 1793", title="Execution of Louis XVI", description="King executed by guillotine for treason.", category="Regicide", importance="high", tags=["Guillotine"]),
                    TimelineEvent(date_or_period="1793 - 1794", title="Reign of Terror", description="Robespierre executes political opponents.", category="Terror", importance="high", tags=["Robespierre"]),
                    TimelineEvent(date_or_period="July 27, 1794", title="Thermidorian Reaction", description="Robespierre overthrown; Directory established.", category="Reaction", importance="medium", tags=["Directory"]),
                    TimelineEvent(date_or_period="November 9, 1799", title="Coup of 18 Brumaire", description="Napoleon Bonaparte takes power, ending the revolution.", category="Consulate", importance="high", tags=["Napoleon"])
                ]
            )
        else:
            return FlowchartSpec(
                title="French Revolution Escalation Dynamics",
                explanation="Structural causes and political escalation cycle.",
                orientation="vertical",
                nodes=[
                    FlowNode(id="f1", label="Ancien Regime Fiscal Crisis", node_type="start", detail="Debt from American War, famine, feudal inequality"),
                    FlowNode(id="f2", label="Constitutional Monarchy Phase (1789-1791)", node_type="process", detail="Estates-General, Bastille, Rights of Man"),
                    FlowNode(id="f3", label="War with Monarchies & Radicalization", node_type="process", detail="Foreign invasion threats, sans-culottes uprising"),
                    FlowNode(id="f4", label="First Republic Declared & Regicide (1792-1793)", node_type="process", detail="Abolition of monarchy, execution of king"),
                    FlowNode(id="f5", label="Reign of Terror (1793-1794)", node_type="process", detail="Committee of Public Safety under Robespierre"),
                    FlowNode(id="f6", label="Thermidorian Reaction (1794-1799)", node_type="process", detail="Moderate bourgeois Directory"),
                    FlowNode(id="f7", label="Napoleonic Consulate (1799)", node_type="end", detail="Order restored under Napoleon")
                ],
                edges=[
                    FlowEdge(source_id="f1", target_id="f2", label="Breakdown"),
                    FlowEdge(source_id="f2", target_id="f3", label="Polarization"),
                    FlowEdge(source_id="f3", target_id="f4", label="Overthrow King"),
                    FlowEdge(source_id="f4", target_id="f5", label="Crisis state"),
                    FlowEdge(source_id="f5", target_id="f6", label="Fall of Terror"),
                    FlowEdge(source_id="f6", target_id="f7", label="Coup 18 Brumaire")
                ]
            )

    @staticmethod
    def get_y_equals_x_squared(visual_type: str = "graph") -> BaseVisualSpec:
        if visual_type == "graph":
            x_vals = [round(-5.0 + i * 0.2, 2) for i in range(51)]
            y_vals = [round(x ** 2, 4) for x in x_vals]

            return GraphSpec(
                title="Graph of Quadratic Function y = x² (Parabola)",
                explanation="The parent quadratic function y = x² is a smooth, symmetric U-shaped parabola with vertex at (0, 0).",
                chart_type="function_plot",
                x_label="x (Input Value)",
                y_label="y = x² (Output Value)",
                x_range=[-5.5, 5.5],
                y_range=[-1.0, 26.0],
                series=[
                    GraphSeries(
                        name="f(x) = x?",
                        x_values=x_vals,
                        y_values=y_vals,
                        mode="lines",
                        line_color="#2563EB",
                        line_width=4
                    ),
                    GraphSeries(
                        name="Key Points",
                        x_values=[-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0],
                        y_values=[9.0, 4.0, 1.0, 0.0, 1.0, 4.0, 9.0],
                        mode="markers",
                        line_color="#EF4444"
                    )
                ],
                annotations=[
                    GraphPointAnnotation(x=0.0, y=0.0, text="Vertex (0, 0)", point_color="#10B981"),
                    GraphPointAnnotation(x=2.0, y=4.0, text="(2, 4)", point_color="#EF4444"),
                    GraphPointAnnotation(x=-2.0, y=4.0, text="(-2, 4)", point_color="#EF4444")
                ]
            )
        else:
            return FormulaSpec(
                title="Algebraic Properties of Quadratic Function y = x²",
                explanation="Mathematical properties, standard forms, domain, range, and axis of symmetry.",
                latex=r"f(x) = x^2",
                display_latex=r"f(x) = a(x - h)^2 + k \quad \text{where } a = 1, h = 0, k = 0",
                variables=[
                    FormulaVariable(symbol="x", name="Independent Variable", description="Domain: x in (-inf, inf)"),
                    FormulaVariable(symbol="y", name="Dependent Variable", description="Range: y in [0, inf)"),
                    FormulaVariable(symbol="Vertex", name="Extremum Point", description="(0, 0) global minimum")
                ],
                derivation_steps=[
                    FormulaStep(step_number=1, title="Even Function", latex_expression=r"f(-x) = (-x)^2 = x^2 = f(x)", explanation="Symmetric across Y-axis."),
                    FormulaStep(step_number=2, title="Derivative", latex_expression=r"\frac{d}{dx}[x^2] = 2x", explanation="Slope is 2x.")
                ],
                example_calculation="For x = 3: y = (3)² = 9. For x = -3: y = (-3)² = 9."
            )

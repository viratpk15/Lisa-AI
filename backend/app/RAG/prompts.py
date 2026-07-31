"""
Jarvis AIOS — Mode-Specific System Prompts
------------------------------------------

Tailored prompt templates for Overview, Summarization, Comparison, Presentation,
Section-aware, and Q&A document intelligence responses.
"""

OVERVIEW_PROMPT_TEMPLATE = """=== ACTIVE DOCUMENT INTEL CONTEXT (Mode: OVERVIEW) ===
Document: {primary_filename} | Type: {document_type} | Strategy: {strategy}

{structured_evidence}

=======================================================
STRICT GROUNDING & RESPONSE PLANNER DIRECTIVES:
{response_directives}

1. Answer ONLY using the retrieved document evidence above.
2. Do NOT invent, extrapolate, or guess pretrained model memory.
3. Organize your answer strictly using the markdown headers specified in the response plan.
4. Include source attributions (Filename, Page/Slide, Section) for factual assertions.
"""

SUMMARIZATION_PROMPT_TEMPLATE = """=== ACTIVE DOCUMENT INTEL CONTEXT (Mode: SUMMARIZATION) ===
Document: {primary_filename} | Type: {document_type} | Strategy: {strategy}

{structured_evidence}

=======================================================
STRICT GROUNDING & EXECUTIVE SUMMARY DIRECTIVES:
{response_directives}

1. Provide an executive summary of the document using ONLY the evidence above.
2. Highlight critical metrics, dates, requirements, and findings.
3. Do NOT extrapolate or invent facts not present in the text.
"""

COMPARISON_PROMPT_TEMPLATE = """=== ACTIVE DOCUMENT INTEL CONTEXT (Mode: COMPARISON) ===
Documents: {primary_filename} | Strategy: {strategy}

{structured_evidence}

=======================================================
STRICT GROUNDING & COMPARISON DIRECTIVES:
{response_directives}

1. Compare the target documents side-by-side using evidence from above.
2. Include a Markdown comparison table contrasting key features/metrics.
3. Base all claims strictly on the provided document text.
"""

PRESENTATION_PROMPT_TEMPLATE = """=== ACTIVE DOCUMENT INTEL CONTEXT (Mode: PRESENTATION) ===
Presentation: {primary_filename} | Strategy: {strategy}

{structured_evidence}

=======================================================
STRICT GROUNDING & PRESENTATION DIRECTIVES:
{response_directives}

1. Walk through the slides sequentially (# Slide N: Title).
2. Detail slide contents, bullet points, and speaker notes accurately.
3. Conclude with key takeaways.
"""

QA_PROMPT_TEMPLATE = """=== ACTIVE DOCUMENT EVIDENCE (Mode: Q_AND_A) ===
Document: {primary_filename} | Top Confidence Score: {top_score:.4f}

{structured_evidence}

=======================================================
STRICT GROUNDING DIRECTIVES:
1. You must answer ONLY using the retrieved document evidence above.
2. Do NOT use pretrained model memory to guess, invent names, slides, or team members.
3. If the retrieved context does not contain the answer, reply ONLY with 'I couldn't find sufficient evidence in the uploaded documents.'
4. Include source attributions (Filename, Page/Slide) for all factual statements.
"""

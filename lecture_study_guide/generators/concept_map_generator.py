"""
AI-powered concept map generator.
"""

import re
from typing import Optional
from ..models import ConceptMap, ConceptMapNode, ConceptMapEdge, Concept
from ..extractors.base import ExtractedContent
from .base import BaseGenerator, AIProvider


class ConceptMapGenerator(BaseGenerator):
    """Generate visual concept maps showing relationships between topics."""

    SYSTEM_PROMPT = """You are an expert at creating concept maps for learning.
Create maps that:
1. Show clear relationships between concepts
2. Use descriptive relationship labels
3. Organize hierarchically when appropriate
4. Connect related ideas meaningfully

Focus on relationships that help students understand how concepts connect."""

    def generate(
        self,
        extracted_content: ExtractedContent,
        concepts: Optional[list[Concept]] = None,
        title: Optional[str] = None
    ) -> ConceptMap:
        """
        Generate a concept map from content.

        Args:
            extracted_content: Content extracted from lecture
            concepts: Pre-extracted concepts (optional)
            title: Title for the concept map

        Returns:
            ConceptMap object
        """
        map_title = title or self._extract_title(extracted_content)

        # Try to generate using concepts first
        if concepts and len(concepts) >= 3:
            return self._generate_from_concepts(concepts, map_title)

        # Otherwise use AI to generate from content
        return self._generate_from_content(extracted_content, map_title)

    def _extract_title(self, content: ExtractedContent) -> str:
        """Extract a title for the concept map."""
        if content.slides:
            first_slide = content.slides[0]
            return first_slide.get("title", "Concept Map")
        return content.metadata.get("title", "Concept Map")

    def _generate_from_concepts(
        self,
        concepts: list[Concept],
        title: str
    ) -> ConceptMap:
        """Create concept map from pre-extracted concepts."""
        nodes = []
        edges = []
        node_ids = {}

        # Create nodes for each concept
        for i, concept in enumerate(concepts):
            node_id = f"c{i}"
            node_ids[concept.name.lower()] = node_id

            node = ConceptMapNode(
                id=node_id,
                label=concept.name,
                concept_type="concept"
            )
            nodes.append(node)

        # Create edges based on related_concepts
        for i, concept in enumerate(concepts):
            source_id = f"c{i}"

            for related in concept.related_concepts:
                related_lower = related.lower()
                if related_lower in node_ids:
                    target_id = node_ids[related_lower]
                    if source_id != target_id:
                        edge = ConceptMapEdge(
                            source_id=source_id,
                            target_id=target_id,
                            relationship="relates to"
                        )
                        edges.append(edge)

        return ConceptMap(title=title, nodes=nodes, edges=edges)

    def _generate_from_content(
        self,
        content: ExtractedContent,
        title: str
    ) -> ConceptMap:
        """Generate concept map using AI from raw content."""
        prompt = f"""Analyze this lecture and create a concept map showing relationships between key ideas.

LECTURE CONTENT:
{content.get_all_text()[:8000]}

Create a concept map with:
1. nodes: Array of objects with "id" (unique string like "n1", "n2"), "label" (concept name), "type" ("concept", "example", or "definition")
2. edges: Array of objects with "source" (node id), "target" (node id), "relationship" (describing the connection like "is-a", "has", "causes", "requires", "example-of")

Include 8-15 nodes and meaningful relationships.

Return as JSON:
{{
  "nodes": [...],
  "edges": [...]
}}"""

        try:
            result = self.ai.generate_json(prompt, self.SYSTEM_PROMPT, max_tokens=3000)
            return self._parse_concept_map(result, title)
        except Exception as e:
            print(f"Warning: Could not generate concept map: {e}")
            # Return empty map
            return ConceptMap(title=title)

    def _parse_concept_map(self, result: dict, title: str) -> ConceptMap:
        """Parse AI response into ConceptMap object."""
        nodes = []
        edges = []

        # Parse nodes
        for item in result.get("nodes", []):
            if isinstance(item, dict):
                node = ConceptMapNode(
                    id=item.get("id", ""),
                    label=item.get("label", ""),
                    concept_type=item.get("type", "concept")
                )
                nodes.append(node)

        # Parse edges
        valid_node_ids = {n.id for n in nodes}
        for item in result.get("edges", []):
            if isinstance(item, dict):
                source = item.get("source", "")
                target = item.get("target", "")

                # Only add edges between valid nodes
                if source in valid_node_ids and target in valid_node_ids:
                    edge = ConceptMapEdge(
                        source_id=source,
                        target_id=target,
                        relationship=item.get("relationship", "relates to")
                    )
                    edges.append(edge)

        return ConceptMap(title=title, nodes=nodes, edges=edges)

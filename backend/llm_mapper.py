# llm_mapper.py

import os
import json
import re
import hashlib
import pandas as pd
from typing import Dict, List
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from .mapping import STANDARD_LINE_ITEMS

load_dotenv()


class LLMMapper:
    """
    Hybrid semantic mapper:
    1. Uses STANDARD_LINE_ITEMS dictionary
    2. Falls back to LLM for unknown labels
    3. Strict JSON validation
    """

    ALLOWED_SECTIONS = {"Revenue", "Expenses", "Profit", "Tax", "Equity", "General"}

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found")

        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=api_key,
            temperature=0
        )

        self.cache = {}

    # ----------------------------------------------------
    # Public API
    # ----------------------------------------------------
    def process_and_map(self, dataframes: List[pd.DataFrame]) -> List[pd.DataFrame]:

        all_labels = pd.concat(
            [df.iloc[:, 0].dropna().astype(str) for df in dataframes]
        ).unique()

        mapping_dict = self.map_labels(list(all_labels))

        enriched = []

        for df in dataframes:
            new_df = df.copy()
            first_col = new_df.columns[0]

            new_df["Original Label"] = new_df[first_col].astype(str)

            new_df["Normalized Label"] = new_df["Original Label"].map(
                lambda x: mapping_dict.get(x, {}).get("normalized", x)
            )

            new_df["Section"] = new_df["Original Label"].map(
                lambda x: mapping_dict.get(x, {}).get("parent_section", "General")
            )

            enriched.append(new_df)

        return enriched

    # ----------------------------------------------------
    # Core Mapping Logic
    # ----------------------------------------------------
    def map_labels(self, labels: List[str]) -> Dict:

        labels = [l.strip() for l in labels if l.strip()]
        mapping = {}

        unknown_labels = []

        for label in labels:
            if label in STANDARD_LINE_ITEMS:
                mapping[label] = {
                    "normalized": STANDARD_LINE_ITEMS[label],
                    "parent_section": self._infer_section(STANDARD_LINE_ITEMS[label])
                }
            else:
                unknown_labels.append(label)

        if unknown_labels:
            llm_mapping = self._call_llm(unknown_labels)
            mapping.update(llm_mapping)

        return mapping

    # ----------------------------------------------------
    # LLM CALL
    # ----------------------------------------------------
    def _call_llm(self, labels: List[str]) -> Dict:

        prompt = self._build_prompt(labels)

        try:
            response = self.llm.invoke(prompt)
            parsed = self._safe_json_parse(response.content)
        except Exception as e:
            print(f"⚠️ LLM call failed: {e}")
            parsed = {}

        # Ensure no hallucinated keys
        cleaned = {}
        for label in labels:
            if label in parsed:
                cleaned[label] = self._validate_structure(label, parsed[label])
            else:
                cleaned[label] = {
                    "normalized": label,
                    "parent_section": "General"
                }

        return cleaned

    # ----------------------------------------------------
    # Prompt Builder
    # ----------------------------------------------------
    def _build_prompt(self, labels: List[str]) -> str:

        reference_rules = "\n".join(
            [f"- '{k}' → '{v}'" for k, v in STANDARD_LINE_ITEMS.items()]
        )

        return f"""
        Standardize these financial labels.

        Preferred mappings:
        {reference_rules}

        Labels:
        {labels}

        Return strict JSON only:
        {{
          "Original Label": {{
              "normalized": "Clean Name",
              "parent_section": "Revenue|Expenses|Profit|Tax|Equity|General"
          }}
        }}
        """

    # ----------------------------------------------------
    # Validators
    # ----------------------------------------------------
    def _safe_json_parse(self, content: str) -> Dict:
        content = re.sub(r"```json|```", "", content).strip()
        try:
            return json.loads(content)
        except:
            return {}

    def _validate_structure(self, original, value):
        if not isinstance(value, dict):
            return {"normalized": original, "parent_section": "General"}

        normalized = value.get("normalized", original)
        section = value.get("parent_section", "General")

        if section not in self.ALLOWED_SECTIONS:
            section = "General"

        return {
            "normalized": normalized,
            "parent_section": section
        }

    def _infer_section(self, label: str) -> str:
        label = label.lower()
        if "revenue" in label:
            return "Revenue"
        if "tax" in label:
            return "Tax"
        if "profit" in label:
            return "Profit"
        if "expense" in label or "cost" in label:
            return "Expenses"
        if "equity" in label:
            return "Equity"
        return "General"

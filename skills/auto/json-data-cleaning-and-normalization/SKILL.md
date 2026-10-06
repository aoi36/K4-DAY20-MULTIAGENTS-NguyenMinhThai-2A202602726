---
name: json-data-cleaning-and-normalization
description: Use when processing, cleaning, and aggregating raw dataset records into standardized CSV and JSON output formats with specific schema and metadata rules.
---
- Convert all monetary values into integer cents (e.g., multiply decimal amounts by 100 and cast to integers) before writing to output files.
- Include the exact required metadata block object containing source file name, total input rows including duplicates, and used rows count.
- Standardize and clean all categorical dimensions to canonical spelling and formatting, and format all timestamps as UTC strings in ISO format.
- Ensure all sorting keys (such as by category/service and timestamp) are properly applied in ascending order before final output generation.
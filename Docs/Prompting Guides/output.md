# Controlling Model Output Formatting

## Overview
You can influence how a model formats its response by defining specific output requirements in system instructions. Common formats include:
- JSON
- Markdown
- Plain text
- HTML
- XML

## Example: Structured vs Unstructured Output

### Scenario
Summarizing customer reviews for a high-end spa business.

### System Instructions with JSON Formatting

````markdown
```json
{
  "pros": [
    "relaxing atmosphere",
    "attentive and efficient staff",
    "high-quality services"
  ],
  "cons": [
    "pricey",
    "no cell phone policy",
    "no refreshments"
  ]
}
```

While the spa has received praise for its tranquil atmosphere, exceptional staff, and top-notch services, there are some areas for improvement. Addressing customer concerns regarding the strict no-cellphone policy and the lack of refreshments could significantly enhance the overall experience. Consider offering a designated area for guests to access their phones if needed, and providing complimentary water or a limited selection of beverages.
````

### System Instructions without Formatting Requirements

```markdown
Pros: The spa provides a tranquil and relaxing atmosphere with high-quality services. Customers rave about the exceptional customer service provided by the staff.

Cons: The spa's no-cellphone policy is a point of contention, with some finding it added to their relaxation and others finding it stressful. Several reviewers found the prices to be high.
```

## Key Differences

| Feature          | JSON Formatted Output | Unformatted Output |
|------------------|-----------------------|--------------------|
| Structure        | Strict hierarchical format | Free-form text |
| Machine Readable | Yes | No |
| Human Readable   | Requires parsing | Immediately readable |
| Additional Notes | Allows for separate analysis section | Combined analysis |
| Integration      | Easy with APIs and databases | Requires parsing for integration |

## Best Practices

1. **Use JSON** when:
   - You need to process the output programmatically
   - You want consistent structure across responses
   - You're integrating with other systems

2. **Use plain text** when:
   - The output is for direct human consumption
   - You don't need to parse specific data points
   - You want more natural language responses

3. **Combine formats** when:
   - You need both structured data and human-readable analysis
   - You're providing data plus recommendations
   - Different consumers need different output types

---

# System Instruction Templates

## JSON Output Template

```markdown
You are a [ROLE]. Follow these instructions, and base your response on the provided User Input.

Instructions:
1. [MAIN TASK]
2. Output your response in JSON format
3. At the very end, outside the JSON object, include [ADDITIONAL ELEMENTS]
4. Keep it concise
5. Stick to the facts
6. Do not hallucinate
7. If there are conflicting opinions, only include the opinion that is recorded the most
8. Do not include any irrelevant information
9. Do not mention any reviewers by name
```

## Plain Text Output Template

```markdown
You are a [ROLE]. Follow these instructions, and base your response on the provided User Input.

Instructions:
1. [MAIN TASK]
2. Keep it concise
3. Stick to the facts
4. Do not hallucinate
5. If there are conflicting opinions, only include the opinion that is recorded the most
6. Do not include any irrelevant information
7. Do not mention any reviewers by name
```

## When to Use Each Template

### JSON Template is Ideal For:
- Data analysis tasks
- API integrations
- Automated processing pipelines
- Structured reporting
- Multi-step workflows

### Plain Text Template is Ideal For:
- Direct customer communications
- Quick summaries
- Human-readable reports
- Casual interactions
- Situations where formatting doesn't matter

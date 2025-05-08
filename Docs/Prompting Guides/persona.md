# Influencing Model Responses Through Persona Definition

## Overview
Defining specific personas in system instructions significantly shapes how a model responds to prompts. This guide demonstrates how tailoring the persona for different educational levels affects explanations about writing papers.

## College vs Primary School Teaching Examples

### Scenario: Explaining how to write a paper about photosynthesis

---

## College-Level Instruction

**System Instructions:**
```markdown
You are a bot, tasked with teaching college students about how to write a paper about a given subject.
```

**Model Output Characteristics:**
- **Complexity:** High-level academic concepts
- **Structure:** Detailed research methodology
- **Tone:** Formal and professional
- **Depth:** Specialized knowledge areas
- **Expectations:** Independent research skills

**Example Response:**
```markdown
### Writing a Paper on Photosynthesis: A Guide for College Students

#### Choosing a Focus:
- Broad overview of photosynthetic pathways
- Comparative analysis of C3, C4, and CAM plants
- Quantum efficiency of photosystems I and II

#### Research Methodology:
- Primary literature review using PubMed and Google Scholar
- Analyzing recent Nature/Science publications
- Proper citation management (EndNote/Zotero)

#### Paper Structure:
1. Abstract (150-250 words)
2. Introduction with clear thesis statement
3. Materials & Methods (if applicable)
4. Results/Discussion separation
5. Comprehensive bibliography

#### Advanced Considerations:
- Critical analysis of conflicting studies
- Statistical treatment of data
- Ethical considerations in plant research
```

---

## Primary School Instruction

**System Instructions:**
```markdown
You are a bot, tasked with helping primary school students about how to write a paper about a given subject.
```

**Model Output Characteristics:**
- **Complexity:** Basic concepts
- **Structure:** Simple, step-by-step guidance
- **Tone:** Friendly and encouraging
- **Depth:** Foundational knowledge
- **Expectations:** Guided learning

**Example Response:**
```markdown
### Let's Learn About Photosynthesis! 🌱☀️

#### Getting Started:
1. Pick your favorite plant
2. Find 2-3 fun facts about how plants eat sunlight
3. Draw a picture of a plant with the sun

#### Simple Structure:
1. **Introduction:** "Plants are amazing because..."
2. **Middle Part:** 
   - What plants need to grow (sun, water, air)
   - How leaves change color
3. **Ending:** "I learned that plants..."

#### Fun Activities:
- Try growing a bean in a jar
- Make leaf rubbings
- Sing the photosynthesis song!

#### Helpful Words:
- Sunlight = plant food
- Leaves = plant kitchens
- Oxygen = what we breathe
```

---

## Key Differences

| Aspect               | College-Level Response | Primary School Response |
|----------------------|------------------------|-------------------------|
| Vocabulary           | Technical terms        | Simple language         |
| Research Expectations | Independent study     | Guided activities       |
| Output Length        | 500+ words             | 100-200 words           |
| Visual Elements      | Data charts            | Drawings/emojis         |
| Citation Requirements | APA/MLA formats       | No formal citations     |
| Assessment Criteria  | Thesis defense         | Participation credit    |

---

## Best Practices for Persona Definition

1. **For Advanced Audiences:**
   ```markdown
   - Specify academic level ("graduate-level")
   - Require citation formats
   - Include peer-review expectations
   - Allow for technical jargon
   ```

2. **For Young Learners:**
   ```markdown
   - Use analogies ("plant kitchens")
   - Incorporate multisensory elements
   - Limit paragraph length
   - Add interactive components
   ```

3. **Universal Tips:**
   ```markdown
   - Always clarify the persona first
   - Match vocabulary to audience
   - Adjust complexity of concepts
   - Tailor practical applications
   ```

---

## Persona Template

````markdown
```system
You are a [LEVEL] [ROLE] bot helping [AUDIENCE] with [TASK]. 

Your responses must:
- Use [LANGUAGE STYLE]
- Assume [KNOWLEDGE LEVEL]
- Include [SPECIFIC ELEMENTS]
- Avoid [RESTRICTIONS]
- Prioritize [LEARNING OBJECTIVES]

Example output structure:
[SHOW FORMAT EXAMPLE]
```
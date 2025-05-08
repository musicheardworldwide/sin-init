# Influencing Model Responses with Contextual Instructions

## Overview
Providing detailed context in system instructions significantly impacts model outputs. This guide demonstrates how structured guidance affects speech writing quality.

## Speech Writing Examples

### Scenario
Writing a high school graduation speech with:
- Event: High School Graduation  
- Audience: [[tools-export-1745623456262.json]],000 people  
- Speaker: Michael Landish, 17-year-old class president  
- Tone: Nostalgic, optimistic  
- Length: 250-500 words  
- Special Considerations: Dyslexia, first-[[sin/1. Initialization/Tools/MCP Server Tools/Time/time]] speaker, favorite teacher mention

---

## With Structured Guidance

**System Instructions:**
```markdown
Help write a speech including:
- Pauses for effect
- Intriguing hook
- Memorable closing
- Appropriate joke
- Personal anecdotes
- Teacher acknowledgment
```

**Model Output:**
```markdown
"Good morning faculty, family, friends, and most importantly, fellow graduates of the class of 2023!

(Pause)

Standing here, looking out at all of you, it feels surreal. Just yesterday, we were freshmen, wide-eyed and a little terrified. Remember those first day jitters? I know I do. I almost tripped and fell carrying my history textbook – a near disaster that would have been immortalised in the halls of [High School Name] history!

(Pause for laughter)

But seriously, look at us now! We've grown up, learned a lot – and I'm not just talking about the Pythagorean Theorem...

[Additional content continues with:]
- Two intentional pauses
- Humorous anecdote hook
- Heartfelt teacher acknowledgment
- Inspirational closing
```

**Key Features:**
✅ Structured pacing with pauses  
✅ Engaging humorous hook  
✅ Personal connection through teacher mention  
✅ Emotional closing remark  
✅ Word count compliance (387 words)  

---

## Without Extra Guidance

**System Instructions:**
```markdown
Help write a speech based on provided information
```

**Model Output:**
```markdown
"Good morning, faculty, family, friends, and most importantly, my fellow graduates...

[Content includes:]
- Generic opening
- Basic timeline reflection
- Teacher acknowledgment
- Future-focused closing
```

**Key Differences:**
✗ No strategic pauses  
✗ Less engaging opening  
✗ Fewer personal touches  
✗ Standard closing  
✗ Shorter length (294 words)  

---

## Comparison Table

| Feature               | With Guidance | Without Guidance |
|-----------------------|---------------|------------------|
| Pacing control        | ✅ Intentional pauses | ✗ Natural flow |
| Audience engagement   | ✅ Humor + personal stories | ✗ Straightforward |
| Emotional impact      | ✅ Strong closing | ✗ Generic ending |
| Personalization       | ✅ Specific anecdotes | ✗ General references |
| Length optimization   | ✅ 387 words | ✗ 294 words |

---

## Best Practices for Speech Writing Prompts

1. **Always specify:**
   ```markdown
   - Desired speech structure
   - Emotional tone
   - Key elements to include
   - Technical requirements (length, pauses)
   ```

2. **Include speaker context:**
   ```markdown
   - Speaking experience level
   - Special considerations (e.g., dyslexia)
   - Personal connections to mention
   ```

3. **Provide examples:**
   ```markdown
   "Include a joke about [specific school experience]"
   "Reference [particular teacher]'s impact"
   ```

4. **Set response boundaries:**
   ```markdown
   "Keep between 250-500 words"
   "Maintain optimistic tone throughout"
   ```

---

## Template for Speech Writing Prompts

````markdown
```system
You are a speechwriting assistant for [EVENT TYPE]. Create speeches that:

1. Open with [HOOK TYPE: joke/story/quote]
2. Include [NUMBER] intentional pauses
3. Last [WORD COUNT] words
4. Mention [SPECIFIC ELEMENTS]
5. Close with [CLOSING TYPE]

Special considerations:
- Speaker has [SPECIAL CHARACTERISTICS]
- Audience is [AUDIENCE PROFILE]
- Avoid [CONTENT RESTRICTIONS]
```
````
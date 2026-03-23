# MLflow Showcase Presentation - Quick Reference Guide

## Presentation Logistics

**Total Duration:** 30 minutes
**Target Audience:** Technical team, developers, data scientists
**Prerequisites:** None (assumes basic Python/ML knowledge)

---

## Time Management

| Section | Duration | Start Time | End Time |
|---------|----------|------------|----------|
| **Introduction** | 3 min | 0:00 | 0:03 |
| **Basics** | 8 min | 0:03 | 0:11 |
| **Intermediate** | 10 min | 0:11 | 0:21 |
| **Advanced** | 7 min | 0:21 | 0:28 |
| **Demo & Q&A** | 2 min | 0:28 | 0:30 |

---

## Section 1: Introduction (3 minutes)

### Key Talking Points

**Problem Statement (1 min):**
- "We deployed an LLM app, but we can't see what's happening"
- No visibility into prompts, responses, performance
- Can't debug multi-step RAG pipelines
- No systematic way to evaluate quality

**Solution Overview (1 min):**
- MLflow GenAI provides complete observability
- Track experiments, trace execution, evaluate quality
- From local development to production deployment
- Open-source, cloud-native, production-ready

**Project Overview (1 min):**
- 3 levels: Basics → Intermediate → Advanced
- 17 working examples with full documentation
- Screenshots, code snippets, real-world patterns
- Ready to run with Zhipu AI GLM-5

### Slide Sequence
1. Title slide
2. Presentation goals
3. Problem vs Solution
4. Project structure

### Transition to Basics
*"Let's start with the foundation and build up from there..."*

---

## Section 2: Basics (8 minutes)

### Key Talking Points

**Overview (1 min):**
- 5 core examples covering MLflow fundamentals
- Focus: Track everything, trace what matters
- Progressive: Simple → Complex

**MLflow Tracking (2 min):**
- Experiments = project folders
- Runs = single executions
- Parameters = configuration
- Metrics = performance
- Artifacts = outputs
- **Show code snippet**

**Tracing Decorators (2 min):**
- `@mlflow.trace` decorator
- Automatic instrumentation
- Tracks inputs, outputs, timing
- **Show code snippet**

**Zhipu + LangChain (2 min):**
- LLM integration patterns
- Chain building with LCEL
- Autologging setup
- **Show code snippet**

**Summary (1 min):**
- You can now track experiments and trace functions
- Foundation for advanced patterns

### Slide Sequence
5. Basics overview
6. MLflow Tracking
7. Tracing Decorators
8. Summary

### Transition to Intermediate
*"Now that we have the foundation, let's explore advanced tracing patterns..."*

---

## Section 3: Intermediate (10 minutes)

### Key Talking Points

**Overview (1 min):**
- 5 advanced patterns
- Focus: From automatic to full control
- Real production patterns

**Manual Span Tracing (2 min):**
- Decorator vs Manual comparison table
- When to use each
- Fine-grained control
- Conditional tracing
- **Show code snippet**

**Nested Spans (2 min):**
- Automatic hierarchies
- Pipeline visualization
- Timing breakdown
- **Show code snippet**

**Distributed Tracing (2 min):**
- Cross-service correlation
- Trace requests across functions
- Microservices patterns
- **Show code snippet**

**LangChain Autologging (2 min):**
- One line to enable
- Zero-code instrumentation
- What gets traced automatically
- **Show code snippet**

**Trace Search (1 min):**
- Programmatic analysis
- Filter and search traces
- Batch processing
- **Show code snippet**

### Slide Sequence
9. Intermediate overview
10. Manual vs Decorator
11. Nested Spans
12. Distributed Tracing
13. LangChain Autologging
14. Trace Search

### Transition to Advanced
*"Now let's see how this applies to real production GenAI applications..."*

---

## Section 4: Advanced (7 minutes)

### Key Talking Points

**Overview (1 min):**
- 7 production applications
- Focus: Production-grade monitoring
- Real-world use cases

**RAG Tracing (1.5 min):**
- The RAG visibility problem
- Explicit chunk tracing
- See retrieved documents
- **Show code snippet**

**RAG Evaluation (1 min):**
- Metrics and comparison
- Chunking strategies
- A/B testing
- **Show metrics table**

**Multi-Turn Conversation (1 min):**
- Memory tracking
- History visualization
- Context management
- **Show code snippet**

**Tool Calling (1 min):**
- Function execution
- Tool selection tracing
- Multi-tool workflows
- **Show code snippet**

**AWS Deployment (1 min):**
- Production architecture
- EKS + RDS + S3
- Cloud-native patterns
- **Show architecture diagram**

**Summary (0.5 min):**
- Complete production stack
- Ready to deploy

### Slide Sequence
15. Advanced overview
16. RAG Tracing
17. RAG Evaluation
18. Multi-Turn Conversation
19. Tool Calling
20. AWS Deployment
21. Summary

### Transition to Demo
*"Let me show you this in action..."*

---

## Section 5: Demo & Q&A (2 minutes)

### Demo Script (1 min)

**Setup (should be done before presentation):**
```bash
# In terminal 1
mlflow ui --backend-store-uri sqlite:///mlflow.db

# In terminal 2 (before presentation)
uv run python src/basics/mlflow_tracking.py
uv run python src/advanced/rag/rag_tracing.py
```

**Live Demo Flow:**

1. **Open MLflow UI**
   - Navigate to http://localhost:5000
   - Show experiment list

2. **Show Basics Run**
   - Click into "mlflow-basics" experiment
   - Show parameters, metrics, artifacts

3. **Show RAG Trace**
   - Navigate to "rag_tracing_demo" run
   - Click on "Traces" section
   - Click into a trace
   - Show span hierarchy
   - Click on "retrieve_documents" span
   - Show retrieved chunks

4. **Show Metrics**
   - Navigate to "rag_evaluation" run
   - Show metrics comparison
   - Show artifacts

**If Demo Fails:**
- Switch to prepared screenshots
- Say "Let me show you what this looks like..."
- Use screenshots from README files

### Q&A (1 min)

**Anticipated Questions:**

**Q: How do we integrate this with our existing app?**
A: Start with `mlflow.langchain.autolog()` - one line gives you instant tracing

**Q: What about non-LangChain apps?**
A: Use `@mlflow.trace` decorator on any function - works with any Python code

**Q: How much overhead does tracing add?**
A: Minimal (~5-10ms per span) - can be disabled in production if needed

**Q: What's the cost for production?**
A: MLflow is open-source. AWS costs depend on scale - typically $100-500/month for small production

**Q: Can we use this with [other LLM provider]?**
A: Yes! MLflow works with OpenAI, Anthropic, HuggingFace, Zhipu, and more

**If you don't know the answer:**
- "That's a great question - let me follow up with you after"
- "I don't have that information handy, but I can find out"

---

## Engagement Tips

### Audience Interaction

**Ask questions throughout:**
- "Who here is using LangChain?" (Show of hands)
- "Who has built a RAG system?" (Show of hands)
- "Who's deployed an LLM app to production?" (Show of hands)

**Pause for understanding:**
- Every 5-7 minutes
- "Does that make sense?"
- "Any questions so far?"

**Use real examples:**
- "Imagine you've built a customer support chatbot..."
- "Think about a RAG system for your company docs..."

### Visual Aids

**Use the projector/monitor:**
- Show MLflow UI live
- Navigate through traces
- Point out specific features

**Use gestures:**
- Indicate hierarchy when talking about spans
- Show "flow" when discussing pipelines
- Point to specific metrics on screen

### Pacing

**Slow down for:**
- Code snippets (let them read it)
- Complex concepts (distributed tracing)
- Key takeaways

**Speed up for:**
- Overview slides
- Lists of features
- Summary points

---

## Common Mistakes to Avoid

### Don't:
- ❌ Read directly from slides
- ❌ Go too fast through code
- ❌ Skip the demo (or have it fail)
- ❌ Run over time
- ❌ Get too technical in details
- ❌ Forget to emphasize practical value

### Do:
- ✅ Make eye contact
- ✅ Use the demo effectively
- ✅ Pause for questions
- ✅ Keep to time
- ✅ Focus on key concepts
- ✅ Show copy-pasteable examples

---

## Backup Plan

### If Demo Fails

**Have ready:**
1. Screenshots in slides
2. Screenshots from README files open
3. Code snippets in editor
4. "Let me show you what this looks like in the screenshots..."

**What to say:**
- "I have screenshots prepared that show exactly what we'd see"
- "The UI looks like this..." (use screenshot)
- "Here's an example of the trace view..." (show screenshot)

### If Running Late

**Skip:**
- Deep dive into any one example
- Extended code explanations
- Backup slides

**Keep:**
- One slide per section
- Key concepts only
- Demo if possible
- Q&A

### If Technical Issues

**Before presentation:**
- Test projector/sound
- Have backup on USB drive
- Print key slides
- Have offline copies

**During presentation:**
- Stay calm
- Use backup screenshots
- Continue with what works
- Don't apologize excessively

---

## Follow-Up Actions

### After Presentation

**Immediate:**
1. Share links to READMEs via email/Slack
2. Distribute presentation slides
3. Offer 1:1 help sessions

**Within 1 week:**
1. Schedule hands-on workshop
2. Set up MLflow instance for team
3. Create team channel for questions

**Within 1 month:**
1. Check on adoption progress
2. Collect feedback
3. Share success stories

### Resources to Share

```
Project Repository: [GitHub URL]
Quick Start Guide: src/basics/README.md
Code Snippets: CODE_SNIPPETS_PLAN.md
Presentation: MLFLOW_KEYNOTE_PRESENTATION.md
```

---

## Presenter Checklist

### 1 Week Before
- [ ] Practice full presentation (time yourself)
- [ ] Prepare demo environment
- [ ] Create backup screenshots
- [ ] Test all code examples
- [ ] Prepare answers to common questions

### 1 Day Before
- [ ] Final practice run
- [ ] Pack presentation on USB drive
- [ ] Print quick reference guide
- [ ] Check equipment compatibility
- [ ] Confirm venue/time

### Day Of Presentation
- [ ] Arrive 15 minutes early
- [ ] Set up demo environment
- [ ] Test projector/sound
- [ ] Open all necessary tabs/files
- [ ] Have water ready
- [ ] Start MLflow UI in background

### During Presentation
- [ ] Make eye contact
- [ ] Monitor time
- [ ] Pause for questions
- [ ] Use demo effectively
- [ ] Keep energy up
- [ ] Stay on schedule

---

## Success Metrics

### Presentation Success Indicators

**During presentation:**
- Audience engaged (nodding, taking notes)
- Questions asked during Q&A
- Positive body language

**After presentation:**
- Team members try the examples
- MLflow adopted for projects
- Follow-up questions asked
- Requests for more detail

**Long-term:**
- MLflow used in production
- Team becomes more observant
- Better Gen systems built
- Documentation referenced regularly

---

## Emergency Contacts

**Technical Support:** [Name/Phone]
**Venue Contact:** [Name/Phone]
**Backup Presenter:** [Name/Phone]

---

**Good luck with your presentation!** 🚀

Remember: You're sharing valuable knowledge that will help your team build better GenAI applications. Focus on the practical value and real-world applications.

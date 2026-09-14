# AI-Powered Customer Support Analytics — Case Study

**Role:** Data Analyst  
**Tools:** SQL, Python, NLP, Power BI 

---

## 1. The Business Problem

Support leaders need to turn unstructured ticket text into actionable intelligence for monitoring service performance, recurring issues, and dissatisfaction risk.

## 2. Dataset & Tools

- **Source:** The Customer Support Ticket Dataset — 8,469 rows, consolidated into a dataset.
- **Data quality:** Missing CSAT and lifecycle fields, placeholder text, unreliable timestamp ordering, and no defensible ticket creation timestamp required checks.
- **Stack:** Python/Pandas for cleaning → NLP for sentiment and topics → scikit-learn for modeling → DuckDB/SQL → Power BI.

## 3. Approach

1. **Data validation** — I profiled row counts, nulls, duplicates, identifiers, categories, and text before analysis. The dataset contained 8,469 tickets with no duplicate Ticket IDs or full-row duplicates.
2. **Definition decisions** — The original escalation-risk concept lacked a defensible escalation label. I therefore clearly defined `is_dissatisfied` from observed CSAT: scores ≤2 as dissatisfied and ≥3 as not dissatisfied, leaving unavailable CSAT missing.
3. **Analysis logic** — I cleaned text, created indicators, built a DuckDB star schema, and integrated sentiment and BERTopic outputs into the SQL KPI layer. This kept observed dissatisfaction separate from risk.
4. **Modeling choice** — I compared Logistic Regression, Balanced Logistic Regression, and Gradient Boosting. Gradient Boosting had the strongest Average Precision (0.4169), so I selected it and used a 0.30 threshold to emphasize recall for human prioritization.
5. **Delivery and validation** — The model trained on 2,769 CSAT-observed tickets and scored 8,469 tickets. A three-page Power BI dashboard was cross-validated against SQL and Python calculations, producing zero KPI discrepancies. This confirmed consistent metrics across layers.

## 4. Key Business Insights

- **8,469 tickets** received complete sentiment, topic, and dissatisfaction-risk outputs, with no missing AI outputs across the final population and consistent downstream coverage.
- **32.70% resolved** established the operational performance baseline for support monitoring and provides useful context for interpreting service outcomes.
- **39.80% observed dissatisfaction** occurred among **2,769 CSAT-observed tickets**, indicating a substantial dissatisfied customer segment within the observed labeled population.
- **91.31% negative sentiment** covered **7,733 tickets**, making text-based issue analysis important for understanding support pressure and recurring customer concerns across the full dataset.
- **91.4% recall and 39.9% precision** were achieved at the 0.30 risk threshold; high recall supports broad review, while precision limits automated interpretation and requires careful human review and judgment.

## 5. Recommendation

Support teams should use the dashboard as a prioritization layer: monitor resolution and observed dissatisfaction, investigate recurring themes through topic and sentiment views, and review higher-risk tickets where capacity allows. The risk score should remain a human-review signal, not an automated decision rule. This matters because the model was trained only on tickets with observed CSAT and its relatively low precision means many flagged tickets will not represent confirmed dissatisfaction. Managers should combine risk signals, ticket context, priority, channel, and established support procedures when deciding which cases deserve attention first. Over time, these reviews can identify where better labels or workflow data would improve future model iterations and support more reliable operational decision-making over time.

## 6. What I'd Do With More Time / More Data

I would add reliable ticket creation timestamps and explicit escalation or SLA outcomes, expand the labeled CSAT population, and validate the model on future holdout data. I would also fine-tune sentiment for support language and validate topics with human labels before production use. Additional labeled outcomes would enable stronger temporal validation, calibration, monitoring, and threshold testing, making the prioritization signal more trustworthy for operations.

---


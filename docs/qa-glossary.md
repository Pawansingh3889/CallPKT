# Call center QA glossary (voice process)

The vocabulary a BPO quality team uses to judge a phone call, collected as the reference for
simulating call center QA on top of CallPKT. Formulas and benchmarks are typical industry values;
every client contract (SLA) defines its own, so treat the numbers as a starting point, not a rule.

## 1. Core terms

| Term | What it means | How it is measured |
|---|---|---|
| **CSAT** (Customer Satisfaction) | How happy the customer was with this interaction. | Post-call survey, usually 1 to 5. CSAT % = satisfied answers (4 or 5) / all answers × 100. |
| **NPS** (Net Promoter Score) | How likely the customer is to recommend the brand. Loyalty, not just this call. | "0 to 10, how likely are you to recommend us?" NPS = % promoters (9 to 10) minus % detractors (0 to 6). Range -100 to +100. |
| **FCR** (First Call Resolution) | The issue was fully solved on the first contact, with no callback or repeat call. | FCR % = issues resolved on first contact / total issues × 100. Often checked by "no repeat call within 24 to 72 hours". |
| **AHT** (Average Handle Time) | Average time an agent spends on one call, end to end. | AHT = (talk time + hold time + after-call work) / calls handled. |
| **QA Calibration** | QAs, team leads, trainers and often the client score the same recorded call separately, then compare and agree, so everyone marks the same way. | Variance between scorers; a common target is within about 5% of each other (COPC guidance), some teams use 10%. |
| **Fatal error** | A mistake so serious the whole call scores 0, whatever else went well. | Binary: present or not. Examples: skipping identity verification, wrong information that costs the customer money, rude behaviour, disconnecting the customer, data privacy breach. |
| **Script deviation** | The agent left out, changed or reordered a mandatory part of the script (greeting, disclosure, verification, closing). Minor wording changes are often allowed; mandatory statements are not. | Marked per scripted step on the scorecard. Missing a legal or compliance statement is usually fatal. |

## 2. Customer experience metrics

| Term | Meaning |
|---|---|
| **DSAT** | Dissatisfied survey (1 or 2 out of 5). QA usually audits every DSAT call to find the cause. |
| **CES** (Customer Effort Score) | How easy it was for the customer to get the issue solved. |
| **Repeat call rate** | % of customers who call again about the same issue within a set window. The opposite of FCR. |
| **Escalation rate** | % of calls handed to a supervisor or higher tier. |
| **Complaint rate** | Formal complaints per number of calls. |
| **Customer sentiment** | Whether the customer's mood moved positive or negative during the call. |

## 3. Handling time and productivity (workforce terms)

| Term | Meaning / formula |
|---|---|
| **Talk time** | Time actually speaking with the customer. |
| **Hold time** | Time the customer was placed on hold. |
| **ACW** (After Call Work) / **Wrap time** | Time after the call for notes, tagging and follow-up actions. |
| **ASA** (Average Speed of Answer) | Average wait before an agent picks up. |
| **Service level** | % of calls answered within a target time. 80/20 = 80% answered within 20 seconds. |
| **Abandonment rate** | % of callers who hang up before reaching an agent. Typical range 3 to 8%. |
| **Occupancy** | Handle time / logged-in time × 100. Often 80 to 85%; higher burns agents out. |
| **Schedule adherence** | Time working as scheduled / scheduled time × 100. Typical target 90 to 95%. |
| **Shrinkage** | % of paid time agents are not available for calls (breaks, training, leave, meetings). |
| **Transfer rate** | % of calls transferred to another team or agent. |
| **Calls per hour (CPH)** | Calls handled per logged-in hour. |
| **SLA** (Service Level Agreement) | The contract between the BPO and the client that fixes targets for all of the above. |

## 4. The QA process

| Term | Meaning |
|---|---|
| **QA scorecard / evaluation form** | The checklist every call is scored against, split into parameters with weightage (points). |
| **Parameter / weightage** | One line on the scorecard (e.g. "Empathy") and how many points it carries. |
| **Quality score** | Points earned / points possible × 100, after fatal errors are applied. |
| **Fatal vs non-fatal** | Fatal makes the whole call 0. Non-fatal only removes that parameter's points. |
| **BCE / CCE / ECE** | Error types used in many Indian BPOs: Business Critical Error (costs the client money or reputation), Customer Critical Error (hurts the customer, e.g. wrong info, rudeness), Compliance Critical Error (breaks law or policy, e.g. privacy). Usually all fatal. |
| **ZTP** (Zero Tolerance Policy) | Behaviours that lead to immediate action, such as abusive language or call avoidance. |
| **Sampling** | Choosing which calls to audit: random sample plus targeted calls (DSAT, long AHT, new hires, bottom performers). Often 4 to 10 calls per agent per week. |
| **Audit** | One QA evaluation of one call. |
| **Live monitoring / silent monitoring** | Listening to a call as it happens, without the agent or customer hearing. |
| **Side-by-side** | QA or team lead sits with the agent and listens in real time, coaching straight after. |
| **Barge-in** | A supervisor joins a live call, usually to rescue it. |
| **Call recording review** | Auditing a recorded call later. The most common QA method. |
| **Dispute / re-evaluation** | The agent or team lead challenges a score; the call is re-checked against the scorecard definition. |
| **Inter-rater reliability** | How consistently different QAs score the same call. Calibration improves it. |
| **Coaching / feedback session** | One-to-one talk with the agent about their audits. Often uses the sandwich method: positive, then the issue, then the action plan. |
| **Action plan** | The specific change the agent agrees to make, with a date to re-check. |
| **TNI** (Training Need Identification) | Using audit trends to decide what training an agent or team needs. |
| **Refresher training** | Short retraining after repeated or fatal errors. |
| **PIP** (Performance Improvement Plan) | Formal plan for agents who stay below target. |
| **Bottom quartile** | The lowest-scoring 25% of agents, who get extra audits and coaching. |
| **Nesting / OJT** | The period after classroom training when new agents take live calls with extra support and audits. |
| **PKT** (Process Knowledge Test) | Test checking that agents know the process and policy. |
| **Mock call** | A practice call with a trainer playing the customer. |
| **RCA** (Root Cause Analysis) | Finding why errors happen, not just that they happen. |
| **5 Whys** | Ask "why" repeatedly until the real cause appears. |
| **Fishbone (Ishikawa) diagram** | Groups possible causes into People, Process, Technology, Policy and so on. |
| **Pareto (80/20)** | The few error types that cause most of the lost points. Fix those first. |
| **Trend analysis** | Quality score and error types tracked week on week, per agent, team and parameter. |
| **Quality huddle** | Short team meeting sharing the week's common errors and best calls. |
| **Best call / call of the week** | A great call shared with the team as an example. |

## 5. Voice call parameters (what QA listens for)

In order of a typical call:

| Parameter | What good looks like | Common errors |
|---|---|---|
| **Opening / greeting** | Brand name, agent name, offer to help, within the first few seconds. | Late opening, missing brand name. |
| **Verification / authentication** | Confirm identity with the required details (KBA: knowledge-based questions) before discussing the account. | Skipping it or partial verification. Usually fatal. |
| **Probing** | Open questions to understand the issue, closed questions to confirm facts. | Assuming the issue, asking things already answered. |
| **Active listening** | Not making the customer repeat themselves. | Asking for details already given. |
| **Paraphrasing** | Repeating the issue back in the agent's words to confirm understanding. | Jumping to a fix before confirming. |
| **Acknowledgement** | Showing the customer was heard ("I understand your order is late"). | Moving on silently. |
| **Empathy** | Recognising the customer's feelings and owning the issue. Empathy ("I can see how frustrating that is") is preferred over sympathy ("sorry to hear that") alone. | Scripted or robotic apology, no empathy at all. |
| **Ownership** | "I will sort this out for you", not passing the blame. | Blaming another team or the customer. |
| **Hold procedure** | Ask permission, give a reason and time estimate, check back every 1 to 2 minutes, thank the customer on return. | Hold without permission, long hold without refresh. |
| **Dead air** | No long silence; keep the customer informed while working ("I'm just checking your order now"). | Silence typically flagged past about 10 to 15 seconds. |
| **Mute misuse** | Mute used instead of proper hold. | Customer hears nothing and thinks the line dropped. |
| **Overtalk / interruption** | Let the customer finish. | Talking over the customer. |
| **Tone and rate of speech** | Calm, friendly, clear, steady pace. | Too fast, flat, irritated or sarcastic tone. |
| **Jargon** | Plain words the customer understands. | Internal codes or technical terms. |
| **Accuracy / resolution** | Correct and complete information, issue solved. | Misinformation, incomplete resolution. Often fatal. |
| **Transfer etiquette** | Warm transfer: explain the reason, brief the next agent before connecting. | Cold or blind transfer, wrong department. |
| **Escalation handling** | Escalate when policy says so, with the case explained. | Refusing a valid escalation, or escalating too early. |
| **Further assistance** | "Is there anything else I can help you with?" | Skipped. |
| **Closing / branding** | Summarise, thank, brand closing line. | Abrupt ending. |
| **Survey solicitation** | Ask for feedback the approved way. | Survey manipulation (asking for a high score). Usually fatal. |
| **Disposition / tagging** | Call tagged with the correct reason code in the system. | Wrong disposition, which corrupts reports. |
| **Documentation / notes** | Clear notes so the next agent does not ask again. | Missing or vague notes. |
| **Call avoidance** | Agent stays on the call until it is resolved or properly ended. | Hanging up on the customer, pretending not to hear. ZTP. |
| **Professionalism** | Courteous at all times. | Rudeness, arguing, abusive language. Fatal / ZTP. |

## 6. Compliance terms (voice)

| Term | Meaning |
|---|---|
| **Call recording disclosure** | Telling the customer the call is recorded, where required. |
| **Data privacy / data protection** | Only share account details with a verified person. India: DPDP Act 2023. UK and EU: GDPR. |
| **PCI DSS** | Card payment rules: card numbers must not be stored or recorded (pause and resume recording). |
| **Mini Miranda** | Mandatory statement in US debt collection calls that the call is an attempt to collect a debt. |
| **DNC** (Do Not Call) | Customers who must not be called for sales (TRAI DND registry in India). |
| **Mandatory disclosure** | Any statement the client or law requires the agent to read word for word. |

## 7. Voice technology and AI QA terms

Relevant to a project like CallPKT, where a bot or an AI scorer is involved.

| Term | Meaning |
|---|---|
| **IVR** (Interactive Voice Response) | The "press 1, press 2" menu before an agent or bot. |
| **ACD** (Automatic Call Distributor) | System that routes incoming calls to the right queue or agent. |
| **CTI** (Computer Telephony Integration) | Links the phone system to the agent's screen (caller details pop up). |
| **ASR / STT** (Speech to Text) | Turning speech into a transcript. CallPKT uses the browser's Web Speech API. |
| **TTS** (Text to Speech) | Turning text into spoken audio. |
| **WER** (Word Error Rate) | % of words the speech recogniser got wrong. High WER makes automated QA unreliable. |
| **Speech analytics** | Automatically analysing recordings for keywords, silence, sentiment and script use. |
| **Auto-QA** | Software scoring every call instead of a small human sample. Still needs calibration against human QAs. |
| **Keyword / phrase spotting** | Checking whether required phrases (greeting, disclosure) or banned phrases were said. |
| **Talk-to-listen ratio** | Share of the call the agent spoke versus the customer. |
| **Silence %** | Share of the call with no one speaking (dead air). |
| **Intent** | What the caller wants (e.g. "track my order"). |
| **Containment rate** | % of calls a bot or IVR fully handles without a human. |
| **Hallucination** | An AI agent stating something false with confidence. In QA terms, misinformation. |

## 8. What a CallPKT transcript can already measure

`app/call_log.py` saves every turn with its role, text and a timestamp, so these can be scored from
`data/calls/*.json` without new recording:

- **AHT** (talk part only): last turn time minus first turn time.
- **Dead air / response gap**: time between a caller turn and the bot's reply.
- **Opening, further assistance, closing, script deviation**: phrase checks on the bot's first and last turns.
- **Accuracy / misinformation, empathy, probing**: need a human or LLM reviewer against a scorecard.
- **CSAT, NPS, FCR**: need a survey or repeat-call data, which the transcript does not hold.

## Sources

- [Call center calibration process, JustCall](https://justcall.io/blog/calibration-process-in-call-center.html)
- [Call calibration, Voxjar glossary](https://voxjar.com/glossary/calibration)
- [Call center quality assurance and QA scorecards, eesel](https://www.eesel.ai/blog/call-center-quality-assurance)
- [Call center QA checklist, IrisAgent](https://irisagent.com/blog/call-center-quality-assurance-checklist/)
- [Call centre KPI calculations, HiveDesk](https://hivedesk.com/resources/call-centre-kpi-calculation)
- [Essential KPIs for BPO contact centers, Brightmetrics](https://support.brightmetrics.com/hc/en-us/articles/37542184482196-Essential-KPIs-for-BPO-Contact-Centers)
- [35 contact center KPIs cheat sheet, Peopleware](https://www.peopleware.com/hubfs/pdfs/infographics/en/35-most-relevant-contact-center-kpis-cheat-sheet.pdf)
- [Call center glossary, Clutch](https://clutch.co/resources/call-center-glossary-67-essential-terms)
- [Contact center glossary, Intradiem](https://intradiem.com/glossary/)

# Synapse Demo Specification

## 1. Product Vision

**Synapse is a real-time, multi-agent arbitration engine that continuously evaluates conflicting multimodal evidence to make split-second operational decisions during enterprise crises.**

*   **The Problem:** During an active cyberattack or fast-moving crisis, humans are too slow to correlate noise, and legacy SIEMs rely on static rules. Waiting 15 seconds for a standard LLM to reason across multiple agents means the network is already lost.
*   **The Buyer:** Chief Information Security Officer (CISO) and Security Operations Center (SOC) Directors.
*   **Why it exists:** Threat actors move at machine speed; enterprise response moves at human speed.
*   **Why existing workflows fail:** Current SOC workflows involve humans manually cross-referencing Slack reports, network telemetry, and firewall logs—taking minutes when milliseconds matter.
*   **Why AI agents are required:** Only AI can synthetically reason across unstructured data (fuzzy Slack messages) and structured data (telemetry) simultaneously.
*   **Why multiple agents are required:** A single agent falls victim to hallucination and context-collapse. Independent parallel agents (Vision, Source, Contradiction, Prediction) force rigorous arbitration, catching flaws before a final decision is made.
*   **Why multimodal reasoning is required:** Crises don't just happen in text logs. They happen in blurry photos of encrypted screens, panicked Slack messages, and live dashboard screenshots.
*   **Why Cerebras speed materially improves the product:** **This is the crux.** If an active ransomware worm is propagating, a traditional ReAct loop running on OpenAI takes 10+ seconds. By the time it recommends "Isolate the Database," the database is already encrypted. Cerebras executes the entire multi-agent quorum in <0.5 seconds, intercepting the attack *before* it jumps subnets. **Latency = Survival.**

---

## 2. Demo Story

**Enterprise Background:** Global FinTech provider handling $5B in daily transactions.
**Company:** "Aegis Financial"
**Stakeholders:** SOC Analysts, VP of Infrastructure.
**Time Pressure:** An active, self-propagating ransomware worm (NotPetya-style) is moving laterally through the network. It takes exactly 4 seconds for the worm to jump from the compromised HR subnet to the primary transaction database.
**Business Impact:** If the database is encrypted, the company loses millions in downtime and regulatory fines.
**Success Condition:** Synapse must correlate conflicting multimodal evidence, achieve consensus, and auto-quarantine the HR subnet *before* the 4-second window closes.

**First 15 Seconds:** The judge sees a live network map and a rapidly updating tick-feed. No typing. Just an onslaught of raw data being instantly digested by six parallel agents, with a confidence graph violently swinging as a fuzzy Slack image contradicts a network log.

---

## 3. Evidence Events

Synapse will process 5 events over 4 seconds.

### Tick 1 (0.0s)
*   **Evidence:** "Helpdesk ticket: My screen just flashed black and all my HR files have a .locked extension."
*   **Source:** IT Service Desk (Text)
*   **Credibility:** Medium (Users often exaggerate).
*   **Expected Impact:** Low confidence, alert triggered.
*   **What changes:** Baseline established. Decision: "Hold & Monitor".

### Tick 2 (0.8s)
*   **Evidence:** Network Telemetry showing abnormal outbound traffic from HR subnet to an unknown Russian IP.
*   **Source:** Firewall Logs (JSON/Text)
*   **Credibility:** High.
*   **Expected Impact:** Confidence rises.
*   **What changes:** Threat level elevated. Prediction agent flags potential lateral movement. Decision: "Prepare Quarantine".

### Tick 3 (1.5s)
*   **Evidence:** Blurry photo uploaded to Slack showing a command prompt with a ransomware ransom note.
*   **Source:** Employee Smartphone (Image)
*   **Credibility:** High, but visually messy.
*   **Expected Impact:** Multimodal Vision agent confirms malware signature. Contradiction agent flags that the firewall log didn't catch the encryption protocol.
*   **What changes:** Massive confidence swing. Decision: "Human Review Required" (due to contradiction).

### Tick 4 (2.2s)
*   **Evidence:** Domain controller logs show rapid, unauthorized credential dumping using Mimikatz from the HR subnet.
*   **Source:** Windows Event Logs (Text)
*   **Credibility:** Absolute.
*   **Expected Impact:** Contradiction resolved. Timeline agent confirms the sequence: Phishing -> Call home -> Credential Dump.
*   **What changes:** Confidence hits 95%. Decision: "Critical Active Breach".

### Tick 5 (3.0s)
*   **Evidence:** Database connection request initiated from HR subnet.
*   **Source:** DB Gateway (Text)
*   **Credibility:** Absolute.
*   **Expected Impact:** Final confirmation of the kill chain.
*   **What changes:** Consensus agent overrides Human Review due to imminent database compromise. Decision: "Auto-Quarantine HR Subnet".

---

## 4. Agent Behaviour

*   **Source Agent:** 
    *   *Responsibility:* Verify the origin of the evidence.
    *   *Input:* Evidence source and context.
    *   *Output:* Reliability score and origin verification.
*   **Vision Agent:**
    *   *Responsibility:* Extract facts from images.
    *   *Input:* Slack photos and dashboard screenshots.
    *   *Output:* OCR text and visual threat classification.
*   **Timeline Agent:**
    *   *Responsibility:* Ensure evidence fits a logical chronological progression.
    *   *Input:* All evidence in the current tick.
    *   *Output:* Chronological consistency check.
*   **Contradiction Agent:**
    *   *Responsibility:* Find flaws across the evidence delta.
    *   *Input:* Current evidence vs. Blackboard history.
    *   *Output:* Flags contradictions (e.g., "Firewall says blocked, but AD logs show successful login").
*   **Prediction Agent:**
    *   *Responsibility:* Forecast the next state.
    *   *Input:* Current accepted state.
    *   *Output:* Threat vector projection (e.g., "Next target: Database").
*   **Consensus Agent:**
    *   *Responsibility:* Final arbitration.
    *   *Input:* The structured JSON outputs of all 5 reasoning agents.
    *   *Output:* Final enterprise decision, global confidence, and human review toggle.

---

## 5. Confidence Evolution

1.  **Tick 1 (40%):** A single user report is unreliable. High uncertainty.
2.  **Tick 2 (65%):** Logs corroborate the user report, but it could still be isolated malware.
3.  **Tick 3 (50%):** A severe drop in confidence. The Vision agent confirms ransomware, but the Contradiction agent panics because standard SOC tools missed the lateral movement signatures. The system flags for Human Review.
4.  **Tick 4 (90%):** Domain controller logs prove the breach is real and lateral movement is occurring. The contradiction is resolved as an advanced evasion technique.
5.  **Tick 5 (98%):** The database is actively targeted. Confidence is near absolute.

*The graph visibly plummets at Tick 3 before skyrocketing at Tick 4. This proves the agents are actually reasoning and arguing, not just accumulating a linear score.*

---

## 6. Decision Evolution

*   **Event 1:** Hold & Monitor
*   **Event 2:** Prepare Quarantine
*   **Event 3:** Human Review Required (System halted due to contradiction)
*   **Event 4:** Critical Active Breach (Human Review overridden by severity)
*   **Event 5:** Auto-Quarantine HR Subnet (Action executed 1 second before DB encryption)

---

## 7. UI Specification

**Theme:** Dark mode, high contrast (Cyan/Red/White), terminal-inspired but polished.
**Layout:**
*   **Left Panel (30%):** Live Evidence Feed (Tick 1-5). Images and logs stream in rapidly.
*   **Center Panel (40%):** The "Brain". Six agent nodes connected in a circular graph around the Consensus node. Pulses when agents complete. 
*   **Right Panel (30%):** 
    *   Top: Confidence Evolution Graph (Live line chart).
    *   Bottom: Decision Evolution Timeline (Auto-scrolling log of final actions).

**Animations:** Extremely fast transitions. The Cerebras speed must be visceral. When a tick hits, the agent nodes flash instantly, and the graph updates flawlessly without lag.

---

## 8. Demo Assets

1.  `ticket_text.txt`: A mock Zendesk/Jira service desk ticket text.
2.  `firewall_log.json`: A mock Palo Alto/Splunk JSON log showing outbound traffic to 185.x.x.x.
3.  `slack_photo.jpg`: A blurry smartphone photo of a monitor displaying a red "Your files are encrypted" ransomware note.
4.  `ad_dump.log`: A Windows Security Event log snippet showing Mimikatz LSASS access.
5.  `db_gateway.txt`: A simple raw text string of a SQL connection request from the compromised IP.

---

## 9. Demo Script (60 Seconds)

*   **[0:00-0:10] Hook:** *"When a network is breached, you don't have 15 seconds for an LLM to think. A ransomware worm jumps subnets in milliseconds. Welcome to Synapse, running on Cerebras."*
*   **[0:10-0:20] Tick 1 & 2:** *"Evidence is streaming into Aegis Financial. An IT ticket and a firewall log arrive. Synapse's 5 independent parallel agents instantly digest this. Confidence is 65%. Decision: Monitor."*
*   **[0:20-0:30] Tick 3 (The Dip):** *"A user uploads this blurry photo to Slack. Watch the graph. Confidence plummets to 50%. The Vision agent confirms ransomware, but the Contradiction agent realizes our firewall missed it. The system halts and requests Human Review."*
*   **[0:30-0:40] Tick 4 (The Spike):** *"But the attack is moving. Active Directory logs flood in. The contradiction is resolved—it's an advanced evasion attack. Confidence spikes to 90%."*
*   **[0:40-0:50] Tick 5 (The Action):** *"The database is targeted. Because Synapse runs on Cerebras, it processes this entire multimodal quorum in under 0.5 seconds. The Consensus agent overrides the human review delay and auto-quarantines the subnet."*
*   **[0:50-1:00] Takeaway:** *"If we ran this on OpenAI, the ReAct loop would take 10 seconds. By the time it finished reasoning, the database would be encrypted. Synapse on Cerebras isn't just faster. Speed is the only reason the product works."*

---

## 10. Implementation Mapping

*   **Backend Changes:** No architecture changes. Update `demo/evidence_player.py` to map to the new SOC scenario timing (10x speed).
*   **Prompts:** Rewrite system prompts for the agents to understand cybersecurity context (firewalls, malware, AD logs).
*   **Assets:** Generate the 5 specific SOC assets (images, logs). Update `crisis_response.json` with the new evidence payloads.
*   **Frontend Changes:** Build the React/Next.js dashboard following the UI Specification. Connect to backend via WebSocket or polling to read the deterministic `DemoRecorder` state.
*   **Validation:** Ensure the playback engine perfectly reproduces the 5-tick SOC scenario with the visible confidence dip at Tick 3.

---

## 11. Validation / Critique

*   **Would this realistically beat 300 submissions?** Yes. It clearly ties the sponsor's unique hardware advantage (Cerebras latency) directly to the product's core value proposition (stopping a cyberattack before encryption). 
*   **Is the buyer obvious?** The CISO/SOC. Very clear budget holder.
*   **Is Cerebras essential?** Absolutely. The 10-second vs 0.5-second distinction is the entire pitch.
*   **Is multimodal genuinely required?** Yes. SOC analysts frequently deal with screenshots of phishing emails or locked screens uploaded by panicked employees.
*   **Is every agent necessary?** Yes. The Contradiction Agent specifically drives the emotional dip in the story.
*   **Does the story create emotional engagement?** Yes, the drop in confidence and the imminent database breach creates high tension.
*   **What are the remaining weaknesses?** Generating realistic cybersecurity logs and ensuring the LLM reliably outputs the expected contradictions during the live playback. This will require strict prompt engineering and potentially forcing specific deterministic paths for the demo to guarantee the 60-second narrative works flawlessly every time.

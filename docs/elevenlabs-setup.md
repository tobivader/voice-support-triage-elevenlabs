# ElevenLabs setup guide

This project is intentionally simple: the Python backend exposes a few clear REST endpoints, and the ElevenLabs agent calls those endpoints through webhook tools.

## 1. Create the agent

In the ElevenLabs dashboard:

- create a new agent;
- set the system prompt to a support triage assistant;
- ask for the customer ID when the user reports an access problem;
- encourage the agent to call the backend instead of inventing account details.

Suggested first prompt:

> Hi, I’m the StreamDesk support assistant. I can help troubleshoot account-access issues. What seems to be happening?

## 2. Add webhook tool: get_customer

Use a GET tool with a URL like:

```text
https://YOUR-RENDER-URL.onrender.com/customers/{customer_id}
```

Path parameter:

- `customer_id` — customer account ID, for example `CUST-102`

The tool description should tell the agent to fetch the customer record before explaining account status.

## 3. Add webhook tool: create_escalation

Use a POST tool with a URL like:

```text
https://YOUR-RENDER-URL.onrender.com/escalations
```

Body fields:

- `customer_id`
- `issue`
- `finding`
- `troubleshooting_performed`

The description should tell the agent to call the escalation tool only when an account issue clearly requires engineering follow-up.

## 4. Test the agent flow

Use the demo IDs:

- `CUST-101`: healthy account
- `CUST-102`: missing entitlement, escalate
- `CUST-103`: inactive subscription, no engineering escalation
- `CUST-999`: unknown customer, verify ID

A successful flow should:

1. ask for the customer ID;
2. call the correct API tool;
3. explain the result in normal language;
4. avoid hallucinating account data;
5. create escalation only in the correct scenarios.

## 5. Public widget

This project includes a placeholder embed in the landing page. Replace the `YOUR_AGENT_ID` value with the public widget ID from the ElevenLabs agent settings.

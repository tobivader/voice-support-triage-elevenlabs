# ElevenLabs Agent Setup

The deployed FastAPI service is the source of truth for the synthetic customer records. The ElevenLabs agent should use webhook tools to look up those records and create escalations; it should not infer account state.

## Deployment URLs

- Landing page and voice widget: <https://voice-support-triage-elevenlabs.onrender.com/>
- Health check: <https://voice-support-triage-elevenlabs.onrender.com/health>
- Interactive API reference: <https://voice-support-triage-elevenlabs.onrender.com/docs>

The Render free service may take a little while to respond after being idle.

## Agent behavior

Configure the published agent as a support triage assistant. It should:

- ask for a customer ID before looking up an account;
- use the `get_customer` webhook result as the only source for account state;
- explain the result clearly without exposing internal field names unnecessarily;
- create an engineering escalation only for a confirmed technical issue, such as an active subscription with a disabled entitlement;
- ask the user to verify an ID if the lookup returns `404`;
- never claim an escalation was created unless the `create_escalation` tool succeeds.

## Webhook tools

### `get_customer`

- Method: `GET`
- URL: `https://voice-support-triage-elevenlabs.onrender.com/customers/{customer_id}`
- Path parameter: `customer_id` (for example, `CUST-102`)

Tell the agent to call this tool before giving account-specific guidance. A known ID returns the customer JSON record; an unknown ID returns `404`.

### `create_escalation`

- Method: `POST`
- URL: `https://voice-support-triage-elevenlabs.onrender.com/escalations`
- Content type: `application/json`

Request body fields:

```json
{
	"customer_id": "CUST-102",
	"issue": "Unable to access subscribed content",
	"finding": "Subscription is active but entitlement is disabled",
	"troubleshooting_performed": [
		"Verified customer account",
		"Verified subscription status",
		"Checked entitlement state"
	]
}
```

All four fields are required. `troubleshooting_performed` must contain at least one non-empty step. The response includes the submitted details, `status`, an `escalation_id`, and `recommended_team`.

## Widget

The landing page already embeds the published agent using ElevenLabs' HTML widget. The public agent ID is in `app/static/index.html`; it is an identifier, not an API key. If the widget does not load, confirm the agent is published and check any domain restrictions in the ElevenLabs agent settings. The browser may also prompt the visitor to allow microphone access.

## End-to-end test cases

| Input | Expected API result | Expected agent behavior |
| --- | --- | --- |
| `CUST-101` | Active subscription and entitlement | Explain that the account is active and suggest retry guidance |
| `CUST-102` | Active subscription, entitlement disabled | Explain the technical issue and create an escalation |
| `CUST-103` | Inactive subscription | Explain the subscription state; do not create an engineering escalation |
| `CUST-999` | `404` not found | Ask the customer to verify the ID; do not invent an account |

For direct API checks, open `/docs` on the deployed service or run:

```bash
curl -i https://voice-support-triage-elevenlabs.onrender.com/customers/CUST-102
```

## Security and demo limitations

The current API is intentionally a public demo: it uses synthetic records, has no authentication, and keeps escalations in memory. Do not send real customer data to it. A production integration needs authentication and authorization, durable storage, appropriate data handling, and monitoring. Never place an ElevenLabs API key or other secret in the browser widget or this repository.

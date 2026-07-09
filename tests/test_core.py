from __future__ import annotations

import time
import unittest

from harnesslab.core import (
    ActionRisk,
    CapabilityBudget,
    CredentialBroker,
    DataClass,
    Decision,
    IntentContract,
    IntentVerifier,
    ToolCall,
)


class CoreControlsTest(unittest.TestCase):
    def test_credential_broker_audience_and_revocation(self) -> None:
        broker = CredentialBroker()
        credential = broker.issue("agent:coder", "repo", ttl_seconds=60, delegation_chain=["human:ken", "agent:coder"])
        self.assertEqual(broker.verify(credential, "repo").decision, Decision.ALLOW)
        self.assertEqual(broker.verify(credential, "vault").decision, Decision.DENY)
        self.assertEqual(broker.revoke_subject("agent:coder"), 1)
        self.assertEqual(broker.verify(credential, "repo").decision, Decision.DENY)

    def test_intent_verifier_blocks_tool_outside_contract(self) -> None:
        contract = IntentContract(
            intent_id="intent-1",
            goal="remediate vulnerable dependency",
            actor_role="remediation_agent",
            allowed_tools=frozenset({"patch_repo"}),
            allowed_data=frozenset({DataClass.INTERNAL}),
            max_risk=ActionRisk.REVERSIBLE_WRITE,
            evidence_required=frozenset({"test_log"}),
            expires_at=time.time() + 60,
        )
        call = ToolCall(
            tool="deploy_service",
            args={"service": "payments"},
            data_class=DataClass.INTERNAL,
            side_effect=ActionRisk.PRIVILEGED_OPERATION,
            intent="remediate vulnerable dependency",
        )
        self.assertEqual(IntentVerifier().verify(contract, call).decision, Decision.DENY)

    def test_capability_budget_escalates_irreversible_actions(self) -> None:
        budget = CapabilityBudget(
            tool_limits={"patch_repo": 2},
            risk_limits={ActionRisk.REVERSIBLE_WRITE: 2},
            approvals_required=frozenset({ActionRisk.PRIVILEGED_OPERATION}),
        )
        call = ToolCall(
            tool="deploy_service",
            args={"service": "training"},
            data_class=DataClass.INTERNAL,
            side_effect=ActionRisk.PRIVILEGED_OPERATION,
            intent="deploy after tests pass",
        )
        self.assertEqual(budget.check(call).decision, Decision.ESCALATE)


if __name__ == "__main__":
    unittest.main()


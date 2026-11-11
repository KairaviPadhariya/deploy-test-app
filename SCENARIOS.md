# Test scenarios (each = one commit + push, or use "Deploy latest commit")

Run them IN ORDER the first time. Scenario 4 needs scenario 1 to be live first,
because the rollback goes back to the previous live deployment.

1. Healthy small commit  -> edit a comment / README line. Expect low risk, deployed, live.
2. Large risky commit    -> run `python make_big_change.py`, commit. Expect higher risk score.
                            If score >= threshold (default 0.5): deployment row status = 'blocked',
                            pipeline_run build_status = 'failed'. NOTE: this is a BLOCK, not a rollback,
                            so rollback_events stays empty. That is expected.
3. Failing tests         -> in tests/test_app.py change `== 200` to `== 500` in test_health.
                            Expect build failed, NOT deployed.
4. Bad release (anomaly) -> in Dockerfile set `ENV SIMULATE_ANOMALY=true`, commit, push. Deploys, then
                            error rate / latency spike; detector rolls back to scenario 1's image.
                            Generate traffic repeatedly: for i in $(seq 1 10); do curl <app-url>/generate-traffic; done
                            This is the ONLY scenario that writes rollback_events automatically
                            (trigger_type = 'anomaly_detected').
5. Manual rollback       -> dashboard "Rollback" button or scripts/rollback.py <deployment_id>
                            (trigger_type = 'manual_cli' / 'manual_api').
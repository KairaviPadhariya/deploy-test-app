# Test scenarios (each = one commit + push, or use "Deploy latest commit")

1. Healthy small commit  -> edit a comment / README line. Expect low risk, deployed, live.
2. Large risky commit    -> run `python make_big_change.py`, commit. Expect higher risk score (many lines/files).
3. Failing tests         -> in tests/test_app.py change `== 200` to `== 500` in test_health. Expect build failed, NOT deployed.
4. Bad release (anomaly) -> in Dockerfile set `ENV SIMULATE_ANOMALY=true`, commit. Deploys, then error rate/latency spike,
                            detector auto-rolls back to scenario 1's image. Generate traffic: curl <app-url>/generate-traffic repeatedly.
5. Manual rollback       -> dashboard "Rollback" button or scripts/rollback.py <deployment_id>.

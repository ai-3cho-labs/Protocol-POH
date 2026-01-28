  . app.tasks.snapshot_task.update_all_tiers

[2026-01-27 18:14:01,937: WARNING/MainProcess] /usr/local/lib/python3.11/site-packages/celery/worker/consumer/consumer.py:507: CPendingDeprecationWarning: The broker_connection_retry configuration setting will no longer determine
whether broker connection retries are made during startup in Celery 6.0 and above.
If you wish to retain the existing behavior for retrying connections on startup,
you should set broker_connection_retry_on_startup to True.
  warnings.warn(

[2026-01-27 18:14:02,036: INFO/MainProcess] Connected to rediss://default:**@divine-prawn-31093.upstash.io:6379//
[2026-01-27 18:14:02,037: WARNING/MainProcess] /usr/local/lib/python3.11/site-packages/celery/worker/consumer/consumer.py:507: CPendingDeprecationWarning: The broker_connection_retry configuration setting will no longer determine
whether broker connection retries are made during startup in Celery 6.0 and above.
If you wish to retain the existing behavior for retrying connections on startup,
you should set broker_connection_retry_on_startup to True.
  warnings.warn(

[2026-01-27 18:14:02,067: INFO/MainProcess] mingle: searching for neighbors
[2026-01-27 18:14:03,168: INFO/MainProcess] mingle: sync with 1 nodes
[2026-01-27 18:14:03,168: INFO/MainProcess] mingle: sync complete
[2026-01-27 18:14:03,326: INFO/MainProcess] celery@0bb6f786 ready.
Instance is healthy
[2026-01-27 18:15:00,016: INFO/MainProcess] Task app.tasks.snapshot_task.take_snapshot[d30b95d2-0721-40e3-bf86-484bd8ba362f] received
[2026-01-27 18:15:00,028: INFO/MainProcess] Task app.tasks.buyback_task.process_creator_rewards[e152deaa-a33e-4042-baf9-3ca839c4baf7] received
[2026-01-27 18:15:00,086: INFO/ForkPoolWorker-2] Created persistent event loop for worker
[2026-01-27 18:15:00,089: INFO/ForkPoolWorker-1] Created persistent event loop for worker
[2026-01-27 18:15:00,169: INFO/ForkPoolWorker-2] HTTP client initialized
[2026-01-27 18:15:01,042: INFO/ForkPoolWorker-1] No pending rewards to process
[2026-01-27 18:15:01,062: INFO/ForkPoolWorker-1] Task app.tasks.buyback_task.process_creator_rewards[e152deaa-a33e-4042-baf9-3ca839c4baf7] succeeded in 1.0315969250000023s: {'status': 'skipped', 'reason': 'no_pending_rewards'}
[2026-01-27 18:15:01,177: INFO/ForkPoolWorker-2] Fetched 45 token holders for mint BXTMChBx...
[2026-01-27 18:15:02,616: INFO/ForkPoolWorker-2] Snapshot taken: id=84228a69-b454-43c7-aeb9-7e913de55f51, holders=44, supply=999989931290833
emitting event "snapshot:taken" to global [/]
[2026-01-27 18:15:02,617: INFO/ForkPoolWorker-2] emitting event "snapshot:taken" to global [/]
emitting event "snapshot:taken" to global [/ws]
[2026-01-27 18:15:02,617: INFO/ForkPoolWorker-2] emitting event "snapshot:taken" to global [/ws]
[2026-01-27 18:15:02,618: INFO/ForkPoolWorker-2] Snapshot taken: 44 holders, supply=999989931290833
[2026-01-27 18:15:02,627: INFO/ForkPoolWorker-2] Task app.tasks.snapshot_task.take_snapshot[d30b95d2-0721-40e3-bf86-484bd8ba362f] succeeded in 2.609542646999998s: {'status': 'success', 'snapshot_id': '84228a69-b454-43c7-aeb9-7e913de55f51', 'holders': 44, 'supply': 999989931290833}
[2026-01-27 18:21:06,120: INFO/MainProcess] Task app.tasks.distribution_task.check_distribution_triggers[05e46579-ae80-4117-8009-3234bd1d7259] received
[2026-01-27 18:21:07,381: INFO/ForkPoolWorker-2] Fetched 7109 token holders for mint GoLDppdj...
[2026-01-27 18:21:08,111: INFO/ForkPoolWorker-2] Fetched 7109 token holders for mint GoLDppdj...
[2026-01-27 18:21:08,395: INFO/ForkPoolWorker-2] Hourly distribution: pool=0.000823, value=$4.21
[2026-01-27 18:21:09,288: INFO/ForkPoolWorker-2] Fetched 7109 token holders for mint GoLDppdj...
[2026-01-27 18:21:10,352: INFO/ForkPoolWorker-2] Fetched 7109 token holders for mint GoLDppdj...
[2026-01-27 18:21:11,103: INFO/ForkPoolWorker-2] Fetched 7109 token holders for mint GoLDppdj...
[2026-01-27 18:21:11,862: INFO/ForkPoolWorker-2] Fetched 7109 token holders for mint GoLDppdj...
[2026-01-27 18:21:11,896: INFO/ForkPoolWorker-2] Batch TWAB: 44 wallets, 44 records (1 excluded)
[2026-01-27 18:21:11,908: INFO/ForkPoolWorker-2] Executing 26 token transfers in 3 batches (batch_size=10)
[2026-01-27 18:21:11,908: INFO/ForkPoolWorker-2] Sending batch 1/3 (10 recipients)
[2026-01-27 18:21:12,221: INFO/ForkPoolWorker-2] Batch transfer sent: 2tHcffncdg79toUAqA9dFtSp3SQQ7RymZwhbuvDNy9WWLGTCe621iaNRNW6mW6HJ66oogucw4gbVFHbEmDXkSWMG (10 recipients)
[2026-01-27 18:21:12,221: INFO/ForkPoolWorker-2] Batch 1 sent: 2tHcffncdg79toUA... (10 recipients)
[2026-01-27 18:21:13,223: INFO/ForkPoolWorker-2] Sending batch 2/3 (10 recipients)
[2026-01-27 18:21:13,366: INFO/ForkPoolWorker-2] Batch transfer sent: 67LEwSTQaUcS9fue4VvxUcN16BSqm9w8ncVTQaPzGLiuwSxnKYLdNRmRuh2bAbn46J2XGX878vvUuM6uurBg6s2N (10 recipients)
[2026-01-27 18:21:13,366: INFO/ForkPoolWorker-2] Batch 2 sent: 67LEwSTQaUcS9fue... (10 recipients)
[2026-01-27 18:21:14,367: INFO/ForkPoolWorker-2] Sending batch 3/3 (6 recipients)
[2026-01-27 18:21:14,519: INFO/ForkPoolWorker-2] Batch transfer sent: 5A192cMRd2YJiyZASiBJbFxoNwHGE85APTNLzpN1ZLKkuz13Pt8T6tGq3HFCY5Rct7Xy6ykPUAGNfqd3VB21ZvLg (6 recipients)
[2026-01-27 18:21:14,520: INFO/ForkPoolWorker-2] Batch 3 sent: 5A192cMRd2YJiyZA... (6 recipients)
[2026-01-27 18:21:14,520: INFO/ForkPoolWorker-2] Batch confirming 3 transactions
[2026-01-27 18:21:14,520: INFO/ForkPoolWorker-2] Batch confirming 3 transactions (timeout=30s)
[2026-01-27 18:21:16,663: INFO/ForkPoolWorker-2] Batch confirmation complete: 3/3 confirmed, 0 timed out
[2026-01-27 18:21:16,664: INFO/ForkPoolWorker-2] Token transfers complete: 26/26 successful
[2026-01-27 18:21:16,706: INFO/ForkPoolWorker-2] Distribution executed: id=c646561e-a194-48c0-84e4-84748db1bfb7, recipients=26, transfers_sent=26, pool=823
emitting event "distribution:executed" to global [/]
[2026-01-27 18:21:16,706: INFO/ForkPoolWorker-2] emitting event "distribution:executed" to global [/]
emitting event "distribution:executed" to global [/ws]
[2026-01-27 18:21:16,706: INFO/ForkPoolWorker-2] emitting event "distribution:executed" to global [/ws]
[2026-01-27 18:21:16,707: INFO/ForkPoolWorker-2] Hourly distribution: success - 823 GOLD to 26 recipients
[2026-01-27 18:21:16,716: INFO/ForkPoolWorker-2] Task app.tasks.distribution_task.check_distribution_triggers[05e46579-ae80-4117-8009-3234bd1d7259] succeeded in 10.594031411000003s: {'status': 'success', 'distribution_id': 'c646561e-a194-48c0-84e4-84748db1bfb7', 'pool_amount': 823, 'recipient_count': 26, 'trigger_type': 'hourly'}
[2026-01-27 18:30:00,203: INFO/MainProcess] Task app.tasks.snapshot_task.update_all_tiers[dca4e8f9-5960-49d0-b73e-c3dd853a51be] received
[2026-01-27 18:30:00,215: INFO/MainProcess] Task app.tasks.buyback_task.process_creator_rewards[91ca1226-46ad-49fa-86ee-0ff100098a00] received
[2026-01-27 18:30:00,955: INFO/ForkPoolWorker-1] No pending rewards to process
[2026-01-27 18:30:00,974: INFO/ForkPoolWorker-1] Task app.tasks.buyback_task.process_creator_rewards[91ca1226-46ad-49fa-86ee-0ff100098a00] succeeded in 0.7577595720000545s: {'status': 'skipped', 'reason': 'no_pending_rewards'}
[2026-01-27 18:30:00,990: INFO/MainProcess] Task app.tasks.snapshot_task.take_snapshot[cb0cbcce-9284-45cb-9f7a-c2ae648c40c7] received
[2026-01-27 18:30:01,052: INFO/ForkPoolWorker-1] HTTP client initialized
[2026-01-27 18:30:01,328: INFO/ForkPoolWorker-1] Fetched 45 token holders for mint BXTMChBx...
[2026-01-27 18:30:01,721: INFO/ForkPoolWorker-2] Tier update complete: 0 wallets upgraded
[2026-01-27 18:30:01,756: INFO/ForkPoolWorker-1] Snapshot taken: id=4aa70f5b-bb81-4fac-938d-f9cb73677ef3, holders=44, supply=999989931290833
emitting event "snapshot:taken" to global [/]
[2026-01-27 18:30:01,757: INFO/ForkPoolWorker-2] Task app.tasks.snapshot_task.update_all_tiers[dca4e8f9-5960-49d0-b73e-c3dd853a51be] succeeded in 1.5528457729999445s: {'status': 'success', 'total_checked': 156, 'upgraded': 0}
[2026-01-27 18:30:01,757: INFO/ForkPoolWorker-1] emitting event "snapshot:taken" to global [/]
emitting event "snapshot:taken" to global [/ws]
[2026-01-27 18:30:01,758: INFO/ForkPoolWorker-1] emitting event "snapshot:taken" to global [/ws]
[2026-01-27 18:30:01,758: INFO/ForkPoolWorker-1] Snapshot taken: 44 holders, supply=999989931290833
[2026-01-27 18:30:01,768: INFO/ForkPoolWorker-1] Task app.tasks.snapshot_task.take_snapshot[cb0cbcce-9284-45cb-9f7a-c2ae648c40c7] succeeded in 0.7774833690000378s: {'status': 'success', 'snapshot_id': '4aa70f5b-bb81-4fac-938d-f9cb73677ef3', 'holders': 44, 'supply': 999989931290833}
[2026-01-27 18:45:00,017: INFO/MainProcess] Task app.tasks.snapshot_task.take_snapshot[80c4165c-5915-4b09-a8c9-ca12bd2f1713] received
[2026-01-27 18:45:00,030: INFO/MainProcess] Task app.tasks.buyback_task.process_creator_rewards[0fbcea89-84cd-4651-b71a-d893d76533fe] received
[2026-01-27 18:45:00,640: INFO/ForkPoolWorker-2] Fetched 45 token holders for mint BXTMChBx...
[2026-01-27 18:45:00,681: INFO/ForkPoolWorker-1] No pending rewards to process
[2026-01-27 18:45:00,714: INFO/ForkPoolWorker-1] Task app.tasks.buyback_task.process_creator_rewards[0fbcea89-84cd-4651-b71a-d893d76533fe] succeeded in 0.6827760280000348s: {'status': 'skipped', 'reason': 'no_pending_rewards'}
[2026-01-27 18:45:01,031: INFO/ForkPoolWorker-2] Snapshot taken: id=e2ea76d5-6624-4b67-95ac-d794b2873b9f, holders=44, supply=999989931290833
emitting event "snapshot:taken" to global [/]
[2026-01-27 18:45:01,032: INFO/ForkPoolWorker-2] emitting event "snapshot:taken" to global [/]
emitting event "snapshot:taken" to global [/ws]
[2026-01-27 18:45:01,032: INFO/ForkPoolWorker-2] emitting event "snapshot:taken" to global [/ws]
[2026-01-27 18:45:01,032: INFO/ForkPoolWorker-2] Snapshot taken: 44 holders, supply=999989931290833
[2026-01-27 18:45:01,041: INFO/ForkPoolWorker-2] Task app.tasks.snapshot_task.take_snapshot[80c4165c-5915-4b09-a8c9-ca12bd2f1713] succeeded in 1.0228160670001216s: {'status': 'success', 'snapshot_id': 'e2ea76d5-6624-4b67-95ac-d794b2873b9f', 'holders': 44, 'supply': 999989931290833}
[2026-01-27 18:47:05,968: INFO/MainProcess] Task app.tasks.buyback_task.process_creator_rewards[91fd4cbc-6ab2-4b09-ad90-210e7b745b92] received
[2026-01-27 18:47:06,180: INFO/ForkPoolWorker-2] No pending rewards to process
[2026-01-27 18:47:06,197: INFO/ForkPoolWorker-2] Task app.tasks.buyback_task.process_creator_rewards[91fd4cbc-6ab2-4b09-ad90-210e7b745b92] succeeded in 0.22811024800012092s: {'status': 'skipped', 'reason': 'no_pending_rewards'}
Instance is stopping.

worker: Warm shutdown (MainProcess)
Instance stopped.
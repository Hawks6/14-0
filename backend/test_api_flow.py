import urllib.request
import json

def api_post(url, data=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8') if data is not None else None,
        headers={'Content-Type': 'application/json'} if data is not None else {},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 0, str(e)

def test_flow():
    # 1. Create session
    status, res = api_post('http://localhost:8000/api/draft/session', {})
    print('Create session status:', status)
    if status != 201:
        print('Error:', res)
        return
    session_id = res['id']
    print('Session ID:', session_id)
    
    # 2. Spin and pick 11 times
    for pick_num in range(11):
        status, res = api_post(f'http://localhost:8000/api/draft/session/{session_id}/spin')
        print(f'Spin {pick_num + 1} status:', status)
        if status != 200:
            print('Error:', res)
            return
        
        # Pick the first player that we can afford and is valid
        players = res['players']
        picked = False
        for p in players:
            p_id = p['player_season_id']
            pick_status, pick_res = api_post(f'http://localhost:8000/api/draft/session/{session_id}/pick', {'player_season_id': p_id})
            if pick_status == 200:
                print(f'Picked player: {p["name"]} for cost {p["credit_cost"]}')
                picked = True
                break
        if not picked:
            print(f'Failed to draft a valid player for pick {pick_num + 1}')
            return

    # 3. Start simulation
    print('Draft completed. Triggering simulation...')
    status, res = api_post(f'http://localhost:8000/api/league/start/{session_id}')
    print('Start league status:', status)
    if status != 201:
        print('Error:', res)
    else:
        print('Simulation started successfully! Matches simulated:', len(res['matches']))

if __name__ == '__main__':
    test_flow()

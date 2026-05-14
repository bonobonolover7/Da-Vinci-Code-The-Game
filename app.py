import streamlit as st
import random
import time

# ==========================================
# 1. 게임 로직 및 초정밀 AI (로직 보강)
# ==========================================
class DavinciCodeLogic:
    @staticmethod
    def init_game():
        if 'deck' not in st.session_state:
            deck = []
            for color in ['B', 'W']:
                for i in range(12):
                    deck.append({'color': color, 'value': str(i), 'revealed': False})
            random.shuffle(deck)
            st.session_state.deck = deck
            st.session_state.player_names = ['나 (User)', '알파봇 1', '알파봇 2', '알파봇 3']
            st.session_state.players = {name: [] for name in st.session_state.player_names}
            st.session_state.turn_idx = 0
            st.session_state.log = ["🎮 게임 시작: 봇이 당신의 패를 노리고 있습니다."]
            st.session_state.status_msg = "게임을 시작합니다!"
            st.session_state.status_type = "info"

            for name in st.session_state.player_names:
                for _ in range(6):
                    st.session_state.players[name].append(st.session_state.deck.pop())
                st.session_state.players[name].sort(key=lambda x: (int(x['value']), 0 if x['color'] == 'B' else 1))

    @staticmethod
    def ai_ultra_think(bot_name):
        known_pool = []
        for name, hand in st.session_state.players.items():
            for t in hand:
                if name == bot_name or t['revealed']:
                    known_pool.append(f"{t['color']}{t['value']}")

        targets = [n for n in st.session_state.player_names if n != bot_name]
        living_targets = [n for n in targets if any(not t['revealed'] for t in st.session_state.players[n])]
        if not living_targets: return None
        
        best_moves = []
        for t_p in living_targets:
            hand = st.session_state.players[t_p]
            for idx, tile in enumerate(hand):
                if tile['revealed']: continue
                min_v, max_v = -1, 12
                for i in range(idx - 1, -1, -1):
                    if hand[i]['revealed']: min_v = int(hand[i]['value']); break
                for i in range(idx + 1, len(hand)):
                    if hand[i]['revealed']: max_v = int(hand[i]['value']); break
                
                candidates = [str(v) for v in range(min_v + 1, max_v) 
                              if f"{tile['color']}{v}" not in known_pool]
                if candidates:
                    best_moves.append({'target': t_p, 'idx': idx, 'guess': random.choice(candidates), 'count': len(candidates)})
        
        if not best_moves: return None
        # 후보가 가장 적은 순서(확률 높은 순서)로 정렬 후 최선의 수 선택
        best_moves.sort(key=lambda x: x['count'])
        return best_moves[0]

    @staticmethod
    def handle_guess(attacker, defender, idx, val):
        target_tile = st.session_state.players[defender][idx]
        if target_tile['value'] == val:
            target_tile['revealed'] = True
            msg = f"🟢 정답! {attacker} → {defender} [{idx+1}번: {val}]"
            st.session_state.status_msg = msg
            st.session_state.status_type = "success"
            st.session_state.log.insert(0, msg)
            return True
        else:
            msg = f"🔴 오답! {attacker} → {defender} [{idx+1}번을 {val}로 추측]"
            st.session_state.status_msg = msg
            st.session_state.status_type = "error"
            st.session_state.log.insert(0, msg)
            return False

# ==========================================
# 2. UI 스타일 (정렬 문제 해결 핵심)
# ==========================================
st.set_page_config(page_title="Davinci Code AI", layout="wide")
DavinciCodeLogic.init_game()

st.markdown("""
    <style>
    .player-row {
        display: flex; align-items: center; padding: 15px;
        margin-bottom: 10px; border-radius: 12px; background: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #eee;
    }
    .active-row { border: 2px solid #00FFAA !important; background: #f0fffb !important; }
    .name-tag { width: 120px; font-weight: bold; font-size: 1.1em; color: #333; }
    .tile-list { display: flex; gap: 8px; flex-wrap: wrap; }
    .tile {
        width: 42px; height: 62px; border-radius: 6px;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; font-weight: bold; border: 2px solid #444;
        transition: transform 0.2s;
    }
    .B { background: #222; color: white; }
    .W { background: #fff; color: #222; }
    .revealed { border-color: #FF4B4B !important; color: #FF4B4B !important; position: relative; }
    .revealed::after { content: '✔'; position: absolute; top: -10px; right: -5px; font-size: 14px; background: #FF4B4B; color: white; border-radius: 50%; width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; }
    </style>
""", unsafe_allow_html=True)

# 상단 알림
if st.session_state.status_type == "success": st.success(st.session_state.status_msg)
elif st.session_state.status_type == "error": st.error(st.session_state.status_msg)
else: st.info(st.session_state.status_msg)

# ==========================================
# 3. 보드 렌더링 (HTML 기반 가로 정렬)
# ==========================================
for name in st.session_state.player_names:
    is_me = (name == '나 (User)')
    is_curr = (name == st.session_state.player_names[st.session_state.turn_idx])
    row_class = "player-row active-row" if is_curr else "player-row"
    
    # 플레이어 한 줄 생성
    html = f'<div class="{row_class}">'
    html += f'<div class="name-tag">{"⭐ " if is_curr else ""}{name}</div>'
    html += '<div class="tile-list">'
    
    for i, t in enumerate(st.session_state.players[name]):
        rev_class = "revealed" if t['revealed'] else ""
        display_val = t['value'] if (t['revealed'] or is_me) else "?"
        html += f'<div class="tile {t["color"]} {rev_class}">{display_val}</div>'
    
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

st.divider()

# ==========================================
# 4. 게임 조작부
# ==========================================
curr_player = st.session_state.player_names[st.session_state.turn_idx]

if curr_player == '나 (User)':
    c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
    with c1:
        target_p = st.selectbox("🎯 공격 대상", [n for n in st.session_state.player_names if n != '나 (User)'])
    with c2:
        # 이미 공개된 타일 제외
        available_indices = [i for i, t in enumerate(st.session_state.players[target_p]) if not t['revealed']]
        t_idx = st.selectbox("📍 타일 위치", available_indices, format_func=lambda x: f"{x+1}번 타일") if available_indices else None
    with c3:
        guess_v = st.text_input("🔢 숫자")
    with c4:
        st.write("")
        if st.button("추리 실행", use_container_width=True) and t_idx is not None:
            if guess_v.isdigit():
                if DavinciCodeLogic.handle_guess('나 (User)', target_p, t_idx, guess_v):
                    pass # 정답이면 한 번 더 (옵션) 혹은 유지
                else:
                    st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
                st.rerun()
else:
    st.subheader(f"🤖 {curr_player}가 계산 중...")
    if st.button(f"{curr_player} 행동 실행", use_container_width=True):
        move = DavinciCodeLogic.ai_ultra_think(curr_player)
        if move:
            st.session_state.log.insert(0, f"🧠 {curr_player} 분석: {move['target']}의 {move['idx']+1}번을 {move['guess']}로 추리 (확률 {100//move['count']}%)")
            if DavinciCodeLogic.handle_guess(curr_player, move['target'], move['idx'], move['guess']):
                pass 
            else:
                st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
            st.rerun()

with st.sidebar:
    st.title("📑 분석 로그")
    for l in st.session_state.log[:15]:
        st.caption(l)
    if st.button("🔄 리셋"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

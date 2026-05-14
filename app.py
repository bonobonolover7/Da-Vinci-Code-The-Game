import streamlit as st
import random

# ==========================================
# 1. 게임 로직 및 초정밀 AI
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
            st.session_state.wrong_guesses = [] 
            st.session_state.turn_idx = 0
            st.session_state.need_penalty = False # 페널티 선택 대기 상태
            st.session_state.log = ["🎮 시스템: 맞히면 한 번 더! 틀리면 공개할 타일을 직접 골라야 합니다."]
            st.session_state.status_msg = "게임을 시작합니다!"
            st.session_state.status_type = "info"

            for name in st.session_state.player_names:
                for _ in range(6):
                    st.session_state.players[name].append(st.session_state.deck.pop())
                st.session_state.players[name].sort(key=lambda x: (int(x['value']), 0 if x['color'] == 'B' else 1))

    @staticmethod
    def ai_ultra_think(bot_name):
        known_pool = [f"{t['color']}{t['value']}" for name, hand in st.session_state.players.items() 
                      for t in hand if name == bot_name or t['revealed']]

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
                              if f"{tile['color']}{v}" not in known_pool and 
                              (t_p, idx, str(v)) not in st.session_state.wrong_guesses]
                if candidates:
                    best_moves.append({'target': t_p, 'idx': idx, 'guess': random.choice(candidates), 'count': len(candidates)})
        
        if not best_moves: return None
        best_moves.sort(key=lambda x: x['count'])
        return best_moves[0]

# ==========================================
# 2. UI 스타일 (오답 글자 빨간색 처리)
# ==========================================
st.set_page_config(page_title="Davinci Code: Combo Mode", layout="wide")
DavinciCodeLogic.init_game()

st.markdown("""
    <style>
    .player-row { display: flex; align-items: center; padding: 12px; margin-bottom: 8px; border-radius: 10px; background: white; border: 1px solid #ddd; }
    .active-row { border: 2px solid #00FFAA !important; background: #f0fffb !important; }
    .name-tag { width: 130px; font-weight: bold; }
    .tile-list { display: flex; gap: 8px; }
    .tile { width: 42px; height: 60px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: bold; border: 2px solid #444; }
    .B { background: #222; color: white; }
    .W { background: #fff; color: #222; }
    /* 오답 글자 강조 스타일 */
    .wrong-text { color: #FF4B4B !important; text-decoration: underline; }
    .revealed { border-color: #FF4B4B !important; background: #fdfdfd; color: #333; }
    .B.revealed { color: #222 !important; background: #e0e0e0; }
    </style>
""", unsafe_allow_html=True)

if st.session_state.status_type == "success": st.success(st.session_state.status_msg)
elif st.session_state.status_type == "error": st.error(st.session_state.status_msg)
else: st.info(st.session_state.status_msg)

# 보드 출력
for name in st.session_state.player_names:
    is_me = (name == '나 (User)')
    is_curr = (name == st.session_state.player_names[st.session_state.turn_idx])
    row_class = "player-row active-row" if is_curr else "player-row"
    
    html = f'<div class="{row_class}"><div class="name-tag">{"⭐" if is_curr else ""}{name}</div><div class="tile-list">'
    for i, t in enumerate(st.session_state.players[name]):
        is_wrong = any(name == target and i == idx for target, idx, val in st.session_state.wrong_guesses)
        rev = "revealed" if t['revealed'] else ""
        val = t['value'] if (t['revealed'] or is_me) else "?"
        
        # 오답 글자 빨간색 처리
        text_style = "wrong-text" if is_wrong and not t['revealed'] else ""
        html += f'<div class="tile {t["color"]} {rev}"><span class="{text_style}">{val}</span></div>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

st.divider()

# ==========================================
# 3. 게임 제어 (Combo & Penalty Select)
# ==========================================
curr_p = st.session_state.player_names[st.session_state.turn_idx]

# --- 페널티 타일 선택 모드 ---
if st.session_state.need_penalty:
    st.warning(f"🚨 추리 실패! {curr_p}님, 공개할 자신의 타일을 선택하세요.")
    avail_my_tiles = [i for i, t in enumerate(st.session_state.players[curr_p]) if not t['revealed']]
    
    if curr_p == '나 (User)':
        p_idx = st.selectbox("공개할 내 타일 번호", avail_my_tiles, format_func=lambda x: f"{x+1}번 타일 ({st.session_state.players[curr_p][x]['value']})")
        if st.button("타일 공개 및 턴 종료"):
            st.session_state.players[curr_p][p_idx]['revealed'] = True
            st.session_state.need_penalty = False
            st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
            st.rerun()
    else:
        # 봇은 가장 낮은 숫자를 페널티로 공개 (전략적 선택)
        if st.button(f"{curr_p}의 페널티 실행"):
            p_idx = random.choice(avail_my_tiles)
            st.session_state.players[curr_p][p_idx]['revealed'] = True
            st.session_state.need_penalty = False
            st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
            st.rerun()

# --- 일반 추리 모드 ---
elif curr_p == '나 (User)':
    st.subheader("🎯 내 차례 (맞히면 한 번 더!)")
    c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
    with c1:
        target_p = st.selectbox("공격 대상", [n for n in st.session_state.player_names if n != '나 (User)'])
    with c2:
        avail = [i for i, t in enumerate(st.session_state.players[target_p]) if not t['revealed']]
        t_idx = st.selectbox("위치", avail, format_func=lambda x: f"{x+1}번") if avail else None
    with c3:
        guess_v = st.text_input("숫자")
    with c4:
        st.write("")
        if st.button("추리!", use_container_width=True) and t_idx is not None:
            target_tile = st.session_state.players[target_p][t_idx]
            if target_tile['value'] == guess_v.strip():
                target_tile['revealed'] = True
                st.session_state.status_msg = f"🟢 정답! 한 번 더 공격하세요."
                st.session_state.status_type = "success"
                st.session_state.log.insert(0, f"✅ 나 (User) 정답! {target_p}의 {t_idx+1}번은 {guess_v}")
            else:
                st.session_state.wrong_guesses.append((target_p, t_idx, guess_v.strip()))
                st.session_state.status_msg = f"🔴 오답! 페널티 타일을 골라야 합니다."
                st.session_state.status_type = "error"
                st.session_state.need_penalty = True
            st.rerun()
else:
    st.subheader(f"🤖 {curr_p}의 차례")
    if st.button(f"{curr_p} 행동 실행"):
        move = DavinciCodeLogic.ai_ultra_think(curr_p)
        if move:
            target_tile = st.session_state.players[move['target']][move['idx']]
            st.session_state.log.insert(0, f"🧠 {curr_p} 추론: {move['target']}의 {move['idx']+1}번을 {move['guess']}로 추리")
            if target_tile['value'] == move['guess']:
                target_tile['revealed'] = True
                st.session_state.status_msg = f"🤖 {curr_p} 정답! 봇이 한 번 더 수행합니다."
                st.session_state.status_type = "success"
            else:
                st.session_state.wrong_guesses.append((move['target'], move['idx'], move['guess']))
                st.session_state.status_msg = f"🤖 {curr_p} 오답! 봇이 페널티를 받습니다."
                st.session_state.status_type = "error"
                st.session_state.need_penalty = True
        st.rerun()

with st.sidebar:
    st.title("📑 분석")
    st.write("**틀린 기록:**")
    for (t, i, v) in st.session_state.wrong_guesses[-5:]:
        st.caption(f"❌ {t} {i+1}번 ≠ {v}")
    if st.button("🔄 리셋"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
